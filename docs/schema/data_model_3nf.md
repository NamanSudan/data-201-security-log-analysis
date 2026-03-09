# 3NF Data Model -- hosts + audit_events

Source notebooks: `01_explore_hosts.ipynb`, `05_explore_audit_intranet.ipynb`, `07_explore_audit_internal_share.ipynb`.
EER diagram (Chen): `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.

---

## 1. Source Files

| # | Notebook | Source path (under russellmitchell/) | Raw table | Rows | Cols | Domain |
|---|---|---|---|---|---|---|
| 1 | 01 | `processing/config/servers.yaml` | `hosts_raw` | 22 | 15 | Host inventory (all 22 testbed machines) |
| 2 | 05 | `gather/intranet_server/logs/audit/audit.log` | `audit_events_intranet_raw` | 2,316 | 40 | Linux auditd -- privilege escalation context |
| 3 | 07 | `gather/internal_share/logs/audit/audit.log` | `audit_events_internal_share_raw` | 732 | 40 | Linux auditd -- data exfiltration context |

Source 2 and 3 use the same auditd format and identical 40-column schema, but come from different hosts with different attack semantics:
- **intranet_server**: SSH login by attacker (172.19.131.174), `su` to jhall, `sudo cat /etc/shadow`. 15 event types, 9 labeled attack lines.
- **internal_share**: Attacker-started exfiltration service (`unit=put`, dnsteal). 11 event types, 2 labeled attack lines.

---

## 2. Entity Catalog

### 2.1 host

Central reference entity. Every machine in the AIT testbed.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| host_id | SERIAL | PK | Surrogate key |
| host_key | VARCHAR(50) | UNIQUE, NOT NULL | YAML dict key (e.g. "intranet-server") |
| hostname | VARCHAR(100) | UNIQUE, NOT NULL | Machine hostname |
| username | VARCHAR(50) | nullable | Only 7 employee hosts |
| openvpn_user | VARCHAR(50) | nullable | Only 3 remote employees |
| default_ipv4_address | VARCHAR(45) | NOT NULL | Single-valued; always 1 per host |
| default_ipv6_address | VARCHAR(45) | NOT NULL | Single-valued; always 1 per host |
| timezone | VARCHAR(10) | NOT NULL | "UTC" for all 22 hosts |
| distribution_id | INT | FK -> distribution | 3NF lookup |

### 2.2 distribution

3NF lookup entity. Eliminates transitive dependency: `distribution_release -> distribution, distribution_version`.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| distribution_id | SERIAL | PK | Surrogate key |
| distribution | VARCHAR(50) | NOT NULL | "Ubuntu" or "Debian" |
| distribution_release | VARCHAR(20) | UNIQUE, NOT NULL | "bionic" or "stretch" (determinant) |
| distribution_version | VARCHAR(20) | NOT NULL | "18.04" or "9.11" |

2 rows total. `distribution_release` is the natural key (candidate key).

### 2.3 host_group

1NF junction entity. Decomposes multi-valued `groups` field.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| host_id | INT | PK, FK -> host | |
| group_name | VARCHAR(50) | PK | 17 distinct groups (adm, sudo, www-data, ...) |

Composite PK (host_id, group_name). Each host has 2-5 groups.

### 2.4 host_fqdn

1NF junction entity. Decomposes multi-valued `fqdns` field.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| host_id | INT | PK, FK -> host | |
| fqdn | VARCHAR(255) | PK | 0-4 FQDNs per host |

Composite PK (host_id, fqdn). Some hosts have 0 FQDNs (NULL in raw -> no rows here).

### 2.5 host_ipv4

1NF junction entity. Decomposes multi-valued `ipv4_addresses` field.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| host_id | INT | PK, FK -> host | |
| ipv4_address | VARCHAR(45) | PK | 21/22 hosts have 1; inet-firewall has 3 |

Composite PK (host_id, ipv4_address).

### 2.6 host_ipv6

1NF junction entity. Decomposes multi-valued `ipv6_addresses` field.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| host_id | INT | PK, FK -> host | |
| ipv6_address | VARCHAR(45) | PK | Same cardinality pattern as ipv4 |

Composite PK (host_id, ipv6_address).

### 2.7 host_log_config

Child entity for the composite+multi-valued `logs` field (already separated during raw loading).

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| config_id | SERIAL | PK | Surrogate key |
| host_id | INT | FK -> host, NOT NULL | |
| log_path | TEXT | NOT NULL | e.g. "/var/log/audit/audit.log" |
| log_type | VARCHAR(50) | NOT NULL | 11 distinct types |
| codec | VARCHAR(20) | nullable | |
| file_chunk_size | INT | nullable | |
| add_field_json | TEXT | nullable | Serialized metadata (4 distinct keys) |

66 rows total (1-9 configs per host).

### 2.8 audit_event (supertype)

Common attributes shared by all audit log event types. Both intranet_server and internal_share rows load into this single table, discriminated by `host_id`.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| event_id | SERIAL | PK | Surrogate key |
| host_id | INT | FK -> host, NOT NULL | Links to source host |
| line_number | INT | NOT NULL | Line in source file (unique per host) |
| type | VARCHAR(20) | NOT NULL | Discriminator (15 distinct across both files) |
| epoch | DOUBLE PRECISION | NOT NULL | Unix timestamp with ms |
| serial | INT | NOT NULL | auditd serial number |
| timestamp | TIMESTAMPTZ | NOT NULL | Derived from epoch (dashed oval in EER) |
| pid | INT | nullable | Process ID |
| uid | INT | nullable | User ID |
| auid | BIGINT | nullable | Audit UID (4294967295 = unset sentinel) |
| ses | BIGINT | nullable | Session ID (4294967295 = unset sentinel) |

3,048 rows total (2,316 from intranet + 732 from internal_share).
Unique constraint on (host_id, line_number) serves as a natural composite key.

### 2.9 audit_pam_event (subtype)

PAM-related event types. Attributes are unpacked from the `msg` TEXT blob (1NF fix).

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event | Shared key with supertype |
| op | VARCHAR(30) | nullable | PAM operation (e.g. PAM:accounting, PAM:setcred) |
| acct | VARCHAR(50) | nullable | Account name |
| exe | TEXT | nullable | Executable path |
| hostname | VARCHAR(50) | nullable | PAM hostname field (not the host entity hostname) |
| addr | VARCHAR(50) | nullable | Source address ("?" or IP) |
| terminal | VARCHAR(30) | nullable | Terminal (cron, ssh, pts0, ...) |
| res | VARCHAR(20) | nullable | Result ("success") |
| cmd | TEXT | nullable | Hex-encoded command (USER_CMD only, 1 event) |
| cwd | TEXT | nullable | Working directory (USER_CMD only) |
| id | INT | nullable | User ID in msg (USER_CMD only) |

Event types: USER_ACCT, CRED_ACQ, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR, USER_LOGIN, USER_CMD.
~2,540 rows (83% of all events). Dominant category.

Note: cmd, cwd, id are specific to USER_CMD (1 event in intranet, 0 in internal_share). They are nullable columns on this subtype rather than a separate subtype due to minimal occurrence.

### 2.10 audit_login_event (subtype)

LOGIN kernel events. Attributes are top-level fields (not from msg blob).

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event | |
| old_auid | BIGINT | nullable | Always 4294967295 in this dataset |
| old_ses | BIGINT | nullable | Always 4294967295 |
| tty | VARCHAR(30) | nullable | "(none)" for LOGIN |
| res | VARCHAR(10) | nullable | "1" (numeric success) |

Event types: LOGIN.
410 rows (304 intranet + 106 internal_share).

### 2.11 audit_service_event (subtype)

Systemd service lifecycle events. Attributes unpacked from `msg` blob (1NF fix).

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event | |
| unit | VARCHAR(100) | nullable | Service unit name (e.g. apt-daily, ssh, **put**) |
| comm | VARCHAR(50) | nullable | Command ("systemd") |
| exe | TEXT | nullable | Executable path |
| hostname | VARCHAR(50) | nullable | Always "?" in this dataset |
| addr | VARCHAR(50) | nullable | Always "?" |
| terminal | VARCHAR(30) | nullable | Always "?" |
| res | VARCHAR(20) | nullable | "success" |

Event types: SERVICE_START, SERVICE_STOP.
555 rows (471 intranet + 84 internal_share). The 2 attack events (unit=put, dnsteal exfiltration) are SERVICE_START/SERVICE_STOP in this subtype.

### 2.12 audit_kernel_event (subtype)

Kernel-level events (AppArmor, syscall, proctitle). Attributes are top-level fields.

| Attribute | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event | |
| apparmor | VARCHAR(20) | nullable | AVC only |
| operation | VARCHAR(30) | nullable | AVC only |
| profile | VARCHAR(50) | nullable | AVC only |
| name | TEXT | nullable | AVC only |
| info | TEXT | nullable | AVC only |
| comm | VARCHAR(50) | nullable | AVC, SYSCALL |
| exe | TEXT | nullable | SYSCALL only |
| arch | VARCHAR(20) | nullable | SYSCALL only |
| syscall | INT | nullable | SYSCALL only |
| success | VARCHAR(5) | nullable | SYSCALL only |
| exit | BIGINT | nullable | SYSCALL only |
| key | VARCHAR(20) | nullable | SYSCALL only |
| proctitle | TEXT | nullable | PROCTITLE only (hex-encoded) |

Event types: AVC, SYSCALL, PROCTITLE.
24 rows (12 intranet + 12 internal_share). All are AppArmor profile_replace events for dhclient, not attack-related.

Note: Within this subtype, AVC/SYSCALL/PROCTITLE each populate different columns. This is residual sparsity within the subtype. Creating 3 separate sub-subtypes for 8 rows each was judged as over-engineering.

---

## 3. Relationships

| Relationship | From | To | Cardinality | Participation | Notes |
|---|---|---|---|---|---|
| belongs_to | host | distribution | N:1 | total (host) : partial (dist) | Every host has exactly 1 distribution |
| has_group | host | host_group | 1:N | total : total | Every host has 2-5 groups |
| has_fqdn | host | host_fqdn | 1:N | partial : total | Some hosts have 0 FQDNs |
| has_ipv4 | host | host_ipv4 | 1:N | total : total | Every host has at least 1 |
| has_ipv6 | host | host_ipv6 | 1:N | total : total | Every host has at least 1 |
| has_log_config | host | host_log_config | 1:N | total : total | Every host has 1-9 log configs |
| generates | host | audit_event | 1:N | partial : total | Only 2 of 22 hosts have audit logs in scope |
| specializes | audit_event | subtypes | total, disjoint | -- | Every event is exactly 1 subtype |

The **generates** relationship is the cross-domain bridge: it connects the host inventory (notebook 01) to the audit events (notebooks 05, 07). The FK `audit_event.host_id` references `host.host_id`. When loading, each audit source file is mapped to its host_id via `host.host_key`:
- `gather/intranet_server/...` -> host_key = "intranet-server"
- `gather/internal_share/...` -> host_key = "internal-share-fileserver"

The **specializes** relationship is a total, disjoint EER specialization. The `type` attribute on audit_event determines which subtype table holds the row's type-specific fields. Every audit_event row has exactly one corresponding row in exactly one subtype table.

---

## 4. Entity Counts

| Entity | Expected rows | Source |
|---|---|---|
| distribution | 2 | Derived from hosts |
| host | 22 | servers.yaml |
| host_group | ~75 | 22 hosts x 2-5 groups each |
| host_fqdn | ~40 | Hosts with FQDNs |
| host_ipv4 | ~26 | 21 hosts x 1 + inet-firewall x 3 |
| host_ipv6 | ~26 | Same pattern |
| host_log_config | 66 | 22 hosts x 1-9 configs |
| audit_event | 3,048 | 2,316 + 732 |
| audit_pam_event | ~2,540 | PAM event types |
| audit_login_event | 410 | LOGIN events |
| audit_service_event | 555 | SERVICE_START + SERVICE_STOP |
| audit_kernel_event | 24 | AVC + SYSCALL + PROCTITLE |

Subtype rows must sum to audit_event rows: ~2,540 + 410 + 555 + 24 = ~3,529. Discrepancy note: the PAM count includes USER_LOGIN (3+0=3 events from intranet only) which also has `msg` blob. Exact counts should be verified during loading. The 4 subtypes are exhaustive and disjoint over the 15 event types.

---

## 5. Loading Order (FK Dependencies)

Tables must be populated in this order due to foreign key constraints:

1. `distribution` (no FK dependencies)
2. `host` (FK -> distribution)
3. `host_group`, `host_fqdn`, `host_ipv4`, `host_ipv6`, `host_log_config` (FK -> host; can load in parallel)
4. `audit_event` (FK -> host)
5. `audit_pam_event`, `audit_login_event`, `audit_service_event`, `audit_kernel_event` (FK -> audit_event; can load in parallel)

---

## 6. UML Class Diagram

```mermaid
classDiagram
    direction TB

    class distribution {
        +int distribution_id PK
        +varchar distribution
        +varchar distribution_release UK
        +varchar distribution_version
    }

    class host {
        +int host_id PK
        +varchar host_key UK
        +varchar hostname UK
        +varchar username
        +varchar openvpn_user
        +varchar default_ipv4_address
        +varchar default_ipv6_address
        +varchar timezone
        +int distribution_id FK
    }

    class host_group {
        +int host_id PK FK
        +varchar group_name PK
    }

    class host_fqdn {
        +int host_id PK FK
        +varchar fqdn PK
    }

    class host_ipv4 {
        +int host_id PK FK
        +varchar ipv4_address PK
    }

    class host_ipv6 {
        +int host_id PK FK
        +varchar ipv6_address PK
    }

    class host_log_config {
        +int config_id PK
        +int host_id FK
        +text log_path
        +varchar log_type
        +varchar codec
        +int file_chunk_size
        +text add_field_json
    }

    class audit_event {
        +int event_id PK
        +int host_id FK
        +int line_number
        +varchar type
        +double epoch
        +int serial
        +timestamptz timestamp
        +int pid
        +int uid
        +bigint auid
        +bigint ses
    }

    class audit_pam_event {
        +int event_id PK FK
        +varchar op
        +varchar acct
        +text exe
        +varchar hostname
        +varchar addr
        +varchar terminal
        +varchar res
        +text cmd
        +text cwd
        +int id
    }

    class audit_login_event {
        +int event_id PK FK
        +bigint old_auid
        +bigint old_ses
        +varchar tty
        +varchar res
    }

    class audit_service_event {
        +int event_id PK FK
        +varchar unit
        +varchar comm
        +text exe
        +varchar hostname
        +varchar addr
        +varchar terminal
        +varchar res
    }

    class audit_kernel_event {
        +int event_id PK FK
        +varchar apparmor
        +varchar operation
        +varchar profile
        +text name
        +text info
        +varchar comm
        +text exe
        +varchar arch
        +int syscall
        +varchar success
        +bigint exit
        +varchar key
        +text proctitle
    }

    host --> distribution : belongs_to N..1
    host "1" --> "*" host_group : has_group
    host "1" --> "*" host_fqdn : has_fqdn
    host "1" --> "*" host_ipv4 : has_ipv4
    host "1" --> "*" host_ipv6 : has_ipv6
    host "1" --> "*" host_log_config : has_log_config
    host "1" --> "*" audit_event : generates
    audit_event <|-- audit_pam_event : subtype
    audit_event <|-- audit_login_event : subtype
    audit_event <|-- audit_service_event : subtype
    audit_event <|-- audit_kernel_event : subtype
```

---

## 7. How to Query Across Domains

Filter audit events by source host:

```sql
SELECT ae.event_id, ae.type, ae.timestamp, ape.op, ape.acct
FROM audit_event ae
JOIN audit_pam_event ape ON ae.event_id = ape.event_id
JOIN host h ON ae.host_id = h.host_id
WHERE h.host_key = 'intranet-server';
```

Find the exfiltration service events:

```sql
SELECT ae.event_id, ae.type, ae.timestamp, ase.unit
FROM audit_event ae
JOIN audit_service_event ase ON ae.event_id = ase.event_id
JOIN host h ON ae.host_id = h.host_id
WHERE h.host_key = 'internal-share-fileserver'
  AND ase.unit = 'put';
```

Get host with its groups and distribution:

```sql
SELECT h.hostname, d.distribution, d.distribution_version, hg.group_name
FROM host h
JOIN distribution d ON h.distribution_id = d.distribution_id
JOIN host_group hg ON h.host_id = hg.host_id
WHERE h.host_key = 'intranet-server';
```
