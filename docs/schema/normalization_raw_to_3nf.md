# Normalization Journey - Raw to 3NF

Step-by-step normalization of raw data from 3 source files into the final 3NF relational schema. Use this as the loading spec when populating the PostgreSQL database.

Reference: `docs/schema/data_model_3nf.md` for the target entity catalog and UML diagram.

---

## Source 1: hosts (Notebook 01)

**Raw file:** `russellmitchell/processing/config/servers.yaml`
**Raw table:** `hosts_raw` (22 rows, 15 columns)
**Domain:** Host inventory for all 22 machines in the AIT testbed.

### Raw State

```
hosts_raw(host_id, host_key, hostname, groups, username, openvpn_user,
          distribution, distribution_release, distribution_version,
          default_ipv4_address, default_ipv6_address,
          ipv4_addresses, ipv6_addresses, fqdns, timezone)
```

Violations present:
- 1NF: `groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses` are multi-valued TEXT blobs
- 1NF: `logs` was already separated during raw loading as `host_log_configs_raw`
- 3NF: `distribution_release -> distribution, distribution_version` (transitive dependency)

### Step 1: 1NF - Decompose Multi-Valued Attributes

Each multi-valued TEXT column becomes a separate junction entity with a composite PK.

**groups -> host_group:**

```
Raw:   groups = "adm,sudo,root"  (TEXT, comma-separated list)
3NF:   host_group(host_id, group_name)
       Row 1: (1, "adm")
       Row 2: (1, "sudo")
       Row 3: (1, "root")
```

Loading logic:
1. For each row in hosts_raw, split `groups` on comma (or parse from YAML list).
2. Insert one row per group value into `host_group`, using the host's `host_id`.

**fqdns -> host_fqdn:**

```
Raw:   fqdns = "intranet.runfaster.xyz,mail.runfaster.xyz"  (TEXT, or NULL)
3NF:   host_fqdn(host_id, fqdn)
```

Loading logic: Same split pattern. Hosts with NULL fqdns produce 0 rows (no insert).

**ipv4_addresses -> host_ipv4:**

```
Raw:   ipv4_addresses = "172.19.131.10,172.19.131.11,172.19.131.12"  (TEXT)
3NF:   host_ipv4(host_id, ipv4_address)
```

Loading logic: Same split pattern. 21 of 22 hosts produce 1 row; inet-firewall produces 3 rows.

Note: `default_ipv4_address` stays on the `host` entity as a simple attribute. It is always single-valued and is a separate field from the multi-valued list. Same for `default_ipv6_address`.

**ipv6_addresses -> host_ipv6:**

Same pattern as ipv4. `host_ipv6(host_id, ipv6_address)`.

**logs (already separated):**

The `logs` field in servers.yaml is a list of dicts (composite + multi-valued). It was already separated during raw loading as `host_log_configs_raw(config_id, host_id, log_path, log_type, codec, file_chunk_size, add_field_json)`. In the 3NF schema this becomes `host_log_config` with the same columns.

After removing the multi-valued columns, the host entity retains:
```
host(host_id, host_key, hostname, username, openvpn_user,
     default_ipv4_address, default_ipv6_address, timezone,
     distribution, distribution_release, distribution_version)
```

### Step 2: 2NF - Check for Partial Dependencies

2NF requires that no non-key attribute depends on only part of a composite key. The `host` entity uses a single-column PK (host_id), so partial dependencies cannot exist.

The junction tables (host_group, host_fqdn, host_ipv4, host_ipv6) have composite PKs, but their only attributes ARE the composite key -- no non-key attributes to be partially dependent.

**2NF: satisfied. No changes needed.**

### Step 3: 3NF - Eliminate Transitive Dependencies

**FD5: distribution_release -> distribution, distribution_version**

This is a transitive dependency: `host_id -> distribution_release -> (distribution, distribution_version)`. A non-key attribute (distribution_release) determines other non-key attributes.

Resolution: Extract into a `distribution` lookup entity.

```
Before:  host(..., distribution, distribution_release, distribution_version, ...)
After:   host(..., distribution_id, ...)
         distribution(distribution_id, distribution, distribution_release, distribution_version)
```

Loading logic:
1. Query distinct (distribution, distribution_release, distribution_version) from hosts_raw. Result: 2 rows.
2. Insert into `distribution` table, getting `distribution_id` for each.
3. For each host, look up its `distribution_release` in the distribution table to get `distribution_id`.
4. Insert into `host` with `distribution_id` FK instead of the 3 raw columns.

**3NF: satisfied after this step.**

### Hosts - Final Field Mapping

| Raw column (hosts_raw) | 3NF target table | 3NF column | Transformation |
|---|---|---|---|
| host_id | host | host_id | Direct (or re-sequence) |
| host_key | host | host_key | Direct |
| hostname | host | hostname | Direct |
| groups | host_group | group_name | Split list, 1 row per value |
| username | host | username | Direct |
| openvpn_user | host | openvpn_user | Direct |
| distribution | distribution | distribution | Deduplicate, insert once per unique combo |
| distribution_release | distribution | distribution_release | Same |
| distribution_version | distribution | distribution_version | Same |
| (derived) | host | distribution_id | FK lookup by distribution_release |
| default_ipv4_address | host | default_ipv4_address | Direct |
| default_ipv6_address | host | default_ipv6_address | Direct |
| ipv4_addresses | host_ipv4 | ipv4_address | Split list, 1 row per value |
| ipv6_addresses | host_ipv6 | ipv6_address | Split list, 1 row per value |
| fqdns | host_fqdn | fqdn | Split list, 1 row per value (skip if NULL) |
| timezone | host | timezone | Direct |

| Raw column (host_log_configs_raw) | 3NF target table | 3NF column | Transformation |
|---|---|---|---|
| config_id | host_log_config | config_id | Direct |
| host_id | host_log_config | host_id | Direct (FK -> host) |
| log_path | host_log_config | log_path | Direct |
| log_type | host_log_config | log_type | Direct |
| codec | host_log_config | codec | Direct |
| file_chunk_size | host_log_config | file_chunk_size | Direct |
| add_field_json | host_log_config | add_field_json | Direct |

---

## Source 2: Audit Log - intranet_server (Notebook 05)

**Raw file:** `russellmitchell/gather/intranet_server/logs/audit/audit.log`
**Raw table:** `audit_events_intranet_raw` (2,316 rows, 40 columns)
**Domain:** Linux auditd events from the intranet server. Contains privilege escalation attack events: SSH login as jhall, `su` to root, `sudo cat /etc/shadow`.
**Labels file:** `russellmitchell/labels/intranet_server/logs/audit/audit.log` (9 labeled lines)

### Raw State

```
audit_events_intranet_raw(row_id, line_number, type, epoch, serial, timestamp,
    pid, uid, auid, ses, msg,
    old_auid, old_ses, tty, res,
    apparmor, operation, info, profile, name,
    comm, exe, arch, syscall, success, exit,
    a0, a1, a2, a3, items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid,
    key, proctitle)
```

15 event types. Each type populates a different subset of the 40 columns. Two violations:

- **1NF:** `msg` TEXT column packs 5-12 key-value pairs into a single blob for PAM and SERVICE events (~86% of rows). Example: `msg='op=PAM:accounting acct="root" exe="/usr/sbin/cron" hostname=? addr=? terminal=cron res=success'`.
- **3NF:** `type -> populated field set`. The event type transitively determines which columns are non-NULL. This is `row_id -> type -> field_set`, a transitive dependency.

### Step 1: 1NF - Unpack the msg Composite Blob

The `msg` column is a composite attribute (one blob per row, not a repeating group). It contains different sub-fields depending on the event type:

**PAM events** (USER_ACCT, CRED_ACQ, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR, USER_LOGIN):
- Sub-fields: `op`, `acct`, `exe`, `hostname`, `addr`, `terminal`, `res`

**USER_CMD events** (1 event in intranet, 0 in internal_share):
- Sub-fields: `cmd` (hex-encoded), `cwd`, `terminal`, `id`

**SERVICE events** (SERVICE_START, SERVICE_STOP):
- Sub-fields: `unit`, `comm`, `exe`, `hostname`, `addr`, `terminal`, `res`

**Other types** (LOGIN, AVC, SYSCALL, PROCTITLE):
- `msg` is NULL. Their fields are top-level columns already.

Parsing logic:
1. For rows where `msg` IS NOT NULL, parse the `msg='...'` string into key-value pairs.
2. Extract each sub-field by key name. Handle quoted values (e.g., `acct="root"`).
3. The parsed sub-fields become columns on the appropriate subtype table (see Step 3).

The `msg` column itself is dropped after parsing - it is fully replaced by atomic sub-field columns.

**1NF: satisfied after parsing.**

### Step 2: 2NF - Check for Partial Dependencies

Single-column PK (event_id). No composite keys in the supertype. 2NF is automatically satisfied.

**2NF: satisfied. No changes needed.**

### Step 3: 3NF - Resolve type -> field_set Transitive Dependency

The transitive dependency `event_id -> type -> field_set` means the `type` column determines which subset of columns are populated. Resolution: disjoint specialization - split into a supertype with common attributes and 4 subtype tables with type-specific attributes.

**Supertype: audit_event**
Common fields present across all/most event types:
```
audit_event(event_id, host_id, line_number, type, epoch, serial, timestamp,
            pid, uid, auid, ses)
```

`host_id` is a new FK column. For intranet_server rows:
- Look up `host_key = 'intranet-server'` in the `host` table to get `host_id`.
- Set `audit_event.host_id` to that value for all 2,316 rows from this file.

**Subtype 1: audit_pam_event**
For event types: USER_ACCT, CRED_ACQ, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR, USER_LOGIN, USER_CMD.
```
audit_pam_event(event_id, op, acct, exe, hostname, addr, terminal, res, cmd, cwd, id)
```
Attributes `op` through `res` come from the parsed `msg` blob (1NF fix). Attributes `cmd`, `cwd`, `id` are USER_CMD-specific (nullable for other PAM types).

**Subtype 2: audit_login_event**
For event type: LOGIN.
```
audit_login_event(event_id, old_auid, old_ses, tty, res)
```
All attributes are top-level raw columns (not from msg blob).

**Subtype 3: audit_service_event**
For event types: SERVICE_START, SERVICE_STOP.
```
audit_service_event(event_id, unit, comm, exe, hostname, addr, terminal, res)
```
All attributes come from the parsed `msg` blob.

**Subtype 4: audit_kernel_event**
For event types: AVC, SYSCALL, PROCTITLE.
```
audit_kernel_event(event_id, apparmor, operation, profile, name, info,
                   comm, exe, arch, syscall, success, exit, key, proctitle)
```
All attributes are top-level raw columns.

**3NF: satisfied after specialization.**

### Intranet - Event Type to Subtype Mapping

| Event type | Count | Subtype table | msg parsed? |
|---|---|---|---|
| USER_ACCT | 305 | audit_pam_event | Yes |
| CRED_ACQ | 308 | audit_pam_event | Yes |
| USER_START | 306 | audit_pam_event | Yes |
| USER_END | 302 | audit_pam_event | Yes |
| CRED_DISP | 302 | audit_pam_event | Yes |
| USER_AUTH | 1 | audit_pam_event | Yes |
| CRED_REFR | 1 | audit_pam_event | Yes |
| USER_LOGIN | 3 | audit_pam_event | Yes |
| USER_CMD | 1 | audit_pam_event | Yes (cmd, cwd, id) |
| LOGIN | 304 | audit_login_event | No (msg is NULL) |
| SERVICE_START | 241 | audit_service_event | Yes |
| SERVICE_STOP | 230 | audit_service_event | Yes |
| AVC | 4 | audit_kernel_event | No (msg is NULL) |
| SYSCALL | 4 | audit_kernel_event | No (msg is NULL) |
| PROCTITLE | 4 | audit_kernel_event | No (msg is NULL) |

### Intranet - Raw Columns to 3NF Mapping

| Raw column | 3NF table | 3NF column | Notes |
|---|---|---|---|
| row_id | - | dropped | Replaced by event_id |
| line_number | audit_event | line_number | Direct |
| type | audit_event | type | Direct (also used as routing discriminator) |
| epoch | audit_event | epoch | Direct |
| serial | audit_event | serial | Direct |
| timestamp | audit_event | timestamp | Direct |
| pid | audit_event | pid | Direct |
| uid | audit_event | uid | Direct |
| auid | audit_event | auid | Direct (4294967295 = unset sentinel) |
| ses | audit_event | ses | Direct (4294967295 = unset sentinel) |
| (new) | audit_event | host_id | FK lookup: host.host_key = 'intranet-server' |
| msg (op) | audit_pam_event | op | Parse from msg blob |
| msg (acct) | audit_pam_event | acct | Parse from msg blob |
| msg (exe) | audit_pam_event | exe | Parse from msg blob |
| msg (hostname) | audit_pam_event | hostname | Parse from msg blob |
| msg (addr) | audit_pam_event | addr | Parse from msg blob |
| msg (terminal) | audit_pam_event | terminal | Parse from msg blob |
| msg (res) | audit_pam_event | res | Parse from msg blob |
| msg (cmd) | audit_pam_event | cmd | Parse from msg blob (USER_CMD only) |
| msg (cwd) | audit_pam_event | cwd | Parse from msg blob (USER_CMD only) |
| msg (id) | audit_pam_event | id | Parse from msg blob (USER_CMD only) |
| old_auid | audit_login_event | old_auid | Direct (LOGIN only) |
| old_ses | audit_login_event | old_ses | Direct (LOGIN only) |
| tty | audit_login_event | tty | Direct (LOGIN only) |
| res | audit_login_event | res | Direct (LOGIN only; "1" = success) |
| msg (unit) | audit_service_event | unit | Parse from msg blob |
| msg (comm) | audit_service_event | comm | Parse from msg blob |
| msg (exe) | audit_service_event | exe | Parse from msg blob |
| msg (hostname) | audit_service_event | hostname | Parse from msg blob |
| msg (addr) | audit_service_event | addr | Parse from msg blob |
| msg (terminal) | audit_service_event | terminal | Parse from msg blob |
| msg (res) | audit_service_event | res | Parse from msg blob |
| apparmor | audit_kernel_event | apparmor | Direct (AVC only) |
| operation | audit_kernel_event | operation | Direct (AVC only) |
| profile | audit_kernel_event | profile | Direct (AVC only) |
| name | audit_kernel_event | name | Direct (AVC only) |
| info | audit_kernel_event | info | Direct (AVC only) |
| comm | audit_kernel_event | comm | Direct (AVC, SYSCALL) |
| exe | audit_kernel_event | exe | Direct (SYSCALL only) |
| arch | audit_kernel_event | arch | Direct (SYSCALL only) |
| syscall | audit_kernel_event | syscall | Direct (SYSCALL only) |
| success | audit_kernel_event | success | Direct (SYSCALL only) |
| exit | audit_kernel_event | exit | Direct (SYSCALL only) |
| key | audit_kernel_event | key | Direct (SYSCALL only) |
| proctitle | audit_kernel_event | proctitle | Direct (PROCTITLE only; hex-encoded) |
| a0, a1, a2, a3 | - | dropped | Register values; low analytical value |
| items | - | dropped | Item count for SYSCALL; low analytical value |
| ppid | - | dropped | Parent PID; low analytical value |
| gid, euid, suid, fsuid, egid, sgid, fsgid | - | dropped | Supplementary IDs; all 0 (root) in this dataset |

Note on dropped columns: `a0`-`a3`, `items`, `ppid`, and the supplementary UID/GID fields (gid, euid, suid, fsuid, egid, sgid, fsgid) appear only in SYSCALL events (4 rows). They are low-value for security analysis in this dataset. If needed, they can be added as nullable columns on `audit_kernel_event`.

---

## Source 3: Audit Log - internal_share (Notebook 07)

**Raw file:** `russellmitchell/gather/internal_share/logs/audit/audit.log`
**Raw table:** `audit_events_internal_share_raw` (732 rows, 40 columns)
**Domain:** Linux auditd events from the internal file share server. Contains data exfiltration attack events: attacker started a service named "put" (dnsteal DNS tunneling tool) to exfiltrate data.
**Labels file:** `russellmitchell/labels/internal_share/logs/audit/audit.log` (2 labeled lines)

### Raw State

Same 40-column schema as intranet_server:
```
audit_events_internal_share_raw(row_id, line_number, type, epoch, serial, timestamp,
    pid, uid, auid, ses, msg, ...)
```

11 event types (subset of intranet's 15 - missing USER_LOGIN, USER_AUTH, USER_CMD, CRED_REFR). Same two violations:
- **1NF:** `msg` TEXT blob, same structure as intranet.
- **3NF:** `type -> field_set`, same transitive dependency.

### Normalization Steps

The normalization steps are identical to Source 2 (intranet_server):
1. **1NF:** Parse `msg` blob into sub-fields.
2. **2NF:** Satisfied (single-column PK).
3. **3NF:** Route to the same 4 subtype tables based on event type.

The key difference is the host_id assignment and the event type distribution.

### internal_share - Event Type to Subtype Mapping

| Event type | Count | Subtype table | msg parsed? |
|---|---|---|---|
| USER_ACCT | 106 | audit_pam_event | Yes |
| CRED_ACQ | 106 | audit_pam_event | Yes |
| USER_START | 106 | audit_pam_event | Yes |
| USER_END | 106 | audit_pam_event | Yes |
| CRED_DISP | 106 | audit_pam_event | Yes |
| LOGIN | 106 | audit_login_event | No |
| SERVICE_START | 47 | audit_service_event | Yes |
| SERVICE_STOP | 37 | audit_service_event | Yes |
| AVC | 4 | audit_kernel_event | No |
| SYSCALL | 4 | audit_kernel_event | No |
| PROCTITLE | 4 | audit_kernel_event | No |

### internal_share - Loading Differences from Intranet

| Aspect | intranet_server | internal_share |
|---|---|---|
| host_id FK lookup | host_key = 'intranet-server' | host_key = 'internal-share-fileserver' |
| Rows | 2,316 | 732 |
| Event types | 15 | 11 (no USER_LOGIN, USER_AUTH, USER_CMD, CRED_REFR) |
| Attack type | Privilege escalation (su, sudo) | Data exfiltration (dnsteal service) |
| Attack labels | 9 lines (escalate, attacker_change_user) | 2 lines (dnsteal, exfiltration-service) |
| Network context | Attacker IP 172.19.131.174 visible in msg hostname/addr | No real IPs (all hostname=?, addr=?) |
| USER_CMD fields | cmd, cwd, id populated (1 row) | Not applicable (0 USER_CMD events) |
| uid values | 0 (root), 33 (www-data), 1002 (jhall) | 0 (root) only |

### internal_share - Raw Column Mapping

Same mapping as intranet (section above), with two differences:
1. `host_id` FK value comes from looking up `host_key = 'internal-share-fileserver'`.
2. Columns `cmd`, `cwd`, `id` on audit_pam_event are always NULL (no USER_CMD events).

---

## Merge Step: Combining Both Audit Sources

Both audit log files load into the SAME set of tables (audit_event + 4 subtypes). The discriminator is `audit_event.host_id`.

### Loading Procedure

```
1. Load hosts first (Source 1) so that host_id values exist.

2. Look up host_ids:
   SELECT host_id FROM host WHERE host_key = 'intranet-server';       - e.g., 5
   SELECT host_id FROM host WHERE host_key = 'internal-share-fileserver'; - e.g., 12

3. Load intranet_server audit events:
   - Parse audit_events_intranet_raw
   - Set host_id = 5 for all rows
   - Insert common fields into audit_event
   - Route type-specific fields to appropriate subtype table

4. Load internal_share audit events:
   - Parse audit_events_internal_share_raw
   - Set host_id = 12 for all rows
   - Insert common fields into audit_event
   - Route type-specific fields to appropriate subtype table
```

### Routing Logic (Pseudocode)

```python
PAM_TYPES = {'USER_ACCT', 'CRED_ACQ', 'USER_START', 'USER_END',
             'CRED_DISP', 'USER_AUTH', 'CRED_REFR', 'USER_LOGIN', 'USER_CMD'}
LOGIN_TYPES = {'LOGIN'}
SERVICE_TYPES = {'SERVICE_START', 'SERVICE_STOP'}
KERNEL_TYPES = {'AVC', 'SYSCALL', 'PROCTITLE'}

for row in raw_table:
    # 1. Insert supertype row
    event_id = insert_audit_event(host_id, row.line_number, row.type,
                                   row.epoch, row.serial, row.timestamp,
                                   row.pid, row.uid, row.auid, row.ses)

    # 2. Route to subtype
    if row.type in PAM_TYPES:
        parsed = parse_msg(row.msg)  # unpack msg blob
        insert_audit_pam_event(event_id, parsed.op, parsed.acct, parsed.exe,
                                parsed.hostname, parsed.addr, parsed.terminal,
                                parsed.res, parsed.get('cmd'), parsed.get('cwd'),
                                parsed.get('id'))

    elif row.type in LOGIN_TYPES:
        insert_audit_login_event(event_id, row.old_auid, row.old_ses,
                                  row.tty, row.res)

    elif row.type in SERVICE_TYPES:
        parsed = parse_msg(row.msg)
        insert_audit_service_event(event_id, parsed.unit, parsed.comm,
                                    parsed.exe, parsed.hostname, parsed.addr,
                                    parsed.terminal, parsed.res)

    elif row.type in KERNEL_TYPES:
        insert_audit_kernel_event(event_id, row.apparmor, row.operation,
                                   row.profile, row.name, row.info,
                                   row.comm, row.exe, row.arch, row.syscall,
                                   row.success, row.exit, row.key, row.proctitle)
```

### Verifying the Merge

After loading both sources, verify:

```sql
-- Total rows should be 3,048
SELECT COUNT(*) FROM audit_event;

-- Per host
SELECT h.host_key, COUNT(*)
FROM audit_event ae JOIN host h ON ae.host_id = h.host_id
GROUP BY h.host_key;
-- Expected: intranet-server = 2316, internal-share-fileserver = 732

-- Subtype completeness (every event has exactly 1 subtype row)
SELECT COUNT(*) FROM audit_event ae
WHERE NOT EXISTS (SELECT 1 FROM audit_pam_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_login_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_service_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_kernel_event WHERE event_id = ae.event_id);
-- Expected: 0 (no orphan supertype rows)
```

---

## Normalization Summary

| Normal form | hosts | audit (intranet) | audit (internal_share) | Resolution |
|---|---|---|---|---|
| **1NF** | groups, fqdns, ipv4_addresses, ipv6_addresses are multi-valued | msg TEXT blob is composite (key-value pairs) | Same as intranet | Multi-valued: junction entities. Composite: parse into atomic columns on subtypes. |
| **2NF** | Satisfied (single-column PK) | Satisfied (single-column PK) | Satisfied | No action needed. |
| **3NF** | distribution_release -> distribution, distribution_version | type -> field_set | Same as intranet | Transitive deps: distribution lookup entity. Event subtypes via disjoint specialization. |

---

## Dual Result Field Note

Two different `res` fields exist in the raw data:
- **PAM/SERVICE events:** `res` is inside the `msg` blob, always text "success". Goes to `audit_pam_event.res` or `audit_service_event.res`.
- **LOGIN events:** `res` is a top-level column, value "1" (numeric string meaning success). Goes to `audit_login_event.res`.

These are semantically the same (operation result) but have different formats. During loading, store as-is. A view or application layer can unify them if needed.

---

## Sentinel Value Note

`auid = 4294967295` and `ses = 4294967295` appear in ~45% of audit events. This is the Linux kernel's "unset" sentinel (0xFFFFFFFF), meaning the process has no associated login session (e.g., cron jobs, systemd services).

Options during loading:
- **Store as-is** (current approach): Keep the integer value. Requires BIGINT column type.
- **Convert to NULL**: Replace sentinel with NULL to indicate "no session". Simplifies queries but loses the distinction between "genuinely NULL" and "unset sentinel".
- **Add boolean flag**: Add `auid_is_set BOOLEAN` derived column. Most explicit but adds columns.

Recommendation: Store as-is in the 3NF tables. Add a view that converts to NULL for analyst convenience.

---

## Complete Loading Order

```
1. distribution           -- no dependencies
2. host                   -- FK -> distribution
3. host_group             \
   host_fqdn               |
   host_ipv4                |-- FK -> host (can load in parallel)
   host_ipv6                |
   host_log_config         /
4. audit_event            -- FK -> host
5. audit_pam_event        \
   audit_login_event       |-- FK -> audit_event (can load in parallel)
   audit_service_event     |
   audit_kernel_event     /
```

Total: 12 tables, 3 loading phases (distribution/host -> junctions -> audit hierarchy).
