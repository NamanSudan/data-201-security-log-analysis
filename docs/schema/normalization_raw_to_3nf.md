# Normalization Journey - Raw to 3NF

Step-by-step normalization of raw source files into a 3NF relational schema in PostgreSQL. This document covers both the staging layer (source-to-staging) and the eventual 3NF transformation (staging-to-3NF).

Reference: `docs/schema/data_model_3nf.md` for the target entity catalog and UML diagram.

## Iteration Scope

**Iteration 1 (complete):** Staging layer. Documents how each raw source file maps into its staging table, including exact column schemas, parsing logic, provenance handling, and loading notes.

**Iteration 2 (complete):** 3NF transformation. Documents how each staging table decomposes into normalized 3NF entities, including DDLs, ETL logic, and verification queries.
- Host domain: complete (see "3NF Transformation: Host Inventory" below).
- Audit domain: complete (see "3NF Transformation: Audit Events" below).
- Labels domain: complete (see "3NF Transformation: Attack Labels" below).

---

## Staging Tables Overview

| # | Source family | Staging table | Source files | Rows | Cols | Notebook(s) |
|---|---|---|---|---|---|---|
| 1 | Host inventory | `stg_host_raw` | 1 YAML | 22 | 15 | 01 |
| 2 | Host log configs | `stg_host_log_config_raw` | (nested in #1) | 66 | 7 | 01 |
| 3 | Audit logs | `stg_audit_line_raw` | 2 audit.log files | 3,048 | 43 | 05, 07 |
| 4 | Attack labels | `stg_attack_label_line_raw` | 8 JSONL files | 61,862 | 6 | 09 |

---

## Source Family 1: Host Inventory (Notebook 01)

### Source File

| Attribute | Value |
|---|---|
| Path | `russellmitchell/processing/config/servers.yaml` |
| Format | YAML dictionary (22 top-level keys) |
| Domain | Host inventory for all 22 machines in the AIT testbed |
| Findings doc | `docs/data_exploration/notebook_findings/naman_hosts_findings.md` |
| ER diagram | `docs/er_diagrams/internal diagrams/hosts_er_v1_raw.drawio.xml` |

### Staging Table: stg_host_raw

**Row-level grain:** One row per host machine. 22 rows total.

**Parsing logic:** Each top-level YAML key becomes one row. The YAML key itself maps to `host_key`. Nested scalar fields map directly to columns. Multi-valued fields (`groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses`) are serialized as JSON array strings via `json.dumps()` and stored in TEXT columns. They are not parsed/exploded at the staging layer. The composite multi-valued `logs` field is separated into `stg_host_log_config_raw` (see below).

**Provenance:** No provenance columns needed - there is only one source file, and `host_key` uniquely identifies each row's origin within the YAML.

**Column schema:**

| # | Column | Type | Nullable | Source field | Notes |
|---|---|---|---|---|---|
| 1 | host_id | SERIAL | PK | (generated) | Surrogate key |
| 2 | host_key | VARCHAR(50) | NOT NULL, UNIQUE | YAML dict key | e.g. "intranet_server", "inet-firewall" |
| 3 | hostname | VARCHAR(100) | NOT NULL, UNIQUE | hostname | Machine hostname |
| 4 | groups | TEXT | NOT NULL | groups | JSON array string, e.g. `["adm","sudo","root"]` (1NF violation, deferred) |
| 5 | username | VARCHAR(50) | nullable | username | Only 7 employee hosts have this |
| 6 | openvpn_user | VARCHAR(50) | nullable | openvpn_user | Only 3 remote employees |
| 7 | distribution | VARCHAR(50) | NOT NULL | distribution | "Ubuntu" or "Debian" |
| 8 | distribution_release | VARCHAR(20) | NOT NULL | distribution_release | "bionic" or "stretch" |
| 9 | distribution_version | VARCHAR(20) | NOT NULL | distribution_version | "18.04" or "9.11" |
| 10 | default_ipv4_address | VARCHAR(45) | NOT NULL | default_ipv4_address | Single-valued; always 1 per host |
| 11 | default_ipv6_address | VARCHAR(45) | NOT NULL | default_ipv6_address | Single-valued; always 1 per host |
| 12 | ipv4_addresses | TEXT | NOT NULL | ipv4_addresses | JSON array string (1NF violation, deferred) |
| 13 | ipv6_addresses | TEXT | NOT NULL | ipv6_addresses | JSON array string (1NF violation, deferred) |
| 14 | fqdns | TEXT | nullable | fqdns | JSON array string; NULL when host has no FQDNs |
| 15 | timezone | VARCHAR(10) | NOT NULL | timezone | "UTC" for all 22 hosts |

**DDL:**

```sql
CREATE TABLE stg_host_raw (
    host_id              SERIAL PRIMARY KEY,
    host_key             VARCHAR(50) NOT NULL UNIQUE,
    hostname             VARCHAR(100) NOT NULL UNIQUE,
    groups               TEXT NOT NULL,
    username             VARCHAR(50),
    openvpn_user         VARCHAR(50),
    distribution         VARCHAR(50) NOT NULL,
    distribution_release VARCHAR(20) NOT NULL,
    distribution_version VARCHAR(20) NOT NULL,
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    ipv4_addresses       TEXT NOT NULL,
    ipv6_addresses       TEXT NOT NULL,
    fqdns                TEXT,
    timezone             VARCHAR(10) NOT NULL
);
```

**Loading notes:**

1. Parse `servers.yaml` with a YAML loader. Each top-level key is one host.
2. For each host dict, extract scalar fields directly into columns.
3. Multi-valued fields (`groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses`): serialize the YAML list to a JSON array string using `json.dumps(info.get("groups", []))`. Do not parse/explode at staging. Iteration 2 ETL will read these back with `json.loads()`.
4. The `logs` nested field is handled separately in `stg_host_log_config_raw`.
5. `host_id` is auto-generated (SERIAL).

**Known normalization violations (for iteration 2):**

- 1NF: `groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses` are multi-valued JSON array strings.
- 3NF: `distribution_release -> distribution, distribution_version` (transitive dependency).

### Staging Table: stg_host_log_config_raw

**Row-level grain:** One row per log configuration entry per host. 66 rows total (1-9 configs per host).

**Parsing logic:** The `logs` field in `servers.yaml` is a list of dicts under each host. Each dict has keys: `path`, `type`, `codec`, `file_chunk_size`, `add_field`. The `add_field` sub-dict is serialized as a JSON string. Each list entry becomes one row, linked to its parent host by `host_id`.

**Column schema:**

| # | Column | Type | Nullable | Source field | Notes |
|---|---|---|---|---|---|
| 1 | config_id | SERIAL | PK | (generated) | Surrogate key |
| 2 | host_id | INT | NOT NULL, FK | (parent host) | References stg_host_raw(host_id) |
| 3 | log_path | TEXT | NOT NULL | path | e.g. "/var/log/audit/audit.log" |
| 4 | log_type | VARCHAR(50) | NOT NULL | type | 11 distinct log types |
| 5 | codec | TEXT | nullable | codec | String or JSON-serialized dict (see note below) |
| 6 | file_chunk_size | INT | nullable | file_chunk_size | |
| 7 | add_field_json | TEXT | nullable | add_field | Serialized JSON string (4 distinct metadata keys) |

**DDL:**

```sql
CREATE TABLE stg_host_log_config_raw (
    config_id      SERIAL PRIMARY KEY,
    host_id        INT NOT NULL REFERENCES stg_host_raw(host_id),
    log_path       TEXT NOT NULL,
    log_type       VARCHAR(50) NOT NULL,
    codec          TEXT,
    file_chunk_size INT,
    add_field_json TEXT
);
```

**Loading notes:**

1. For each host in `servers.yaml`, iterate over the `logs` list.
2. Insert one row per log config entry, setting `host_id` to the parent host's surrogate key.
3. `add_field` dict is serialized to JSON string.
4. `codec` is usually a plain string (e.g. `"json"`), but at least one entry in servers.yaml has a nested dict value (`{"json": {"ecs_compatibility": "disabled"}}`). The staging parser serializes dict codec values to JSON text via `json.dumps()`, so the column type is `TEXT` rather than `VARCHAR(20)`.
5. Load after `stg_host_raw` (FK dependency).

**Known normalization violations (for iteration 2):**

- `add_field_json` is a serialized JSON blob. Decide in iteration 2 whether to decompose into a separate key-value table.

---

## Source Family 2: Audit Logs (Notebooks 05, 07)

### Source Files

Both files share the same Linux auditd format and load into a single shared staging table.

| # | Host | Source path (under russellmitchell/) | Rows | Event types | Attack context | Notebook |
|---|---|---|---|---|---|---|
| 1 | intranet_server | `gather/intranet_server/logs/audit/audit.log` | 2,316 | 15 | Privilege escalation (su, sudo) | 05 |
| 2 | internal_share | `gather/internal_share/logs/audit/audit.log` | 732 | 11 | Data exfiltration (dnsteal service) | 07 |

**Total:** 3,048 rows in shared staging table.

**Findings docs:**
- `docs/data_exploration/notebook_findings/naman_audit_intranet_findings.md`
- `docs/data_exploration/notebook_findings/naman_audit_internal_share_findings.md`

**ER diagram:** `docs/er_diagrams/internal diagrams/audit_events_er_v1_raw.drawio.xml`

### Staging Table: stg_audit_line_raw (shared)

Both audit source files load into this single table. The `source_host` and `source_log` provenance columns distinguish records from different sources.

**Row-level grain:** One row per line in the source audit.log file. Line number is 1-based within each source file.

**Parsing logic (per source file):**

Each line in the audit.log file is a single auditd record in key=value format. Parsing steps:

1. Read the file line by line. Each line becomes one row.
2. Store the full original line as `raw_line` (provenance).
3. Extract the `type=` field from the `audit(epoch:serial)` header.
4. Parse `epoch` and `serial` from the audit header timestamp format `audit(1642782073.123:456)`.
5. Derive `timestamp` from `epoch` (TSTZ).
6. Extract all top-level key=value pairs into their respective columns (pid, uid, auid, ses, old_auid, old_ses, tty, res, apparmor, operation, info, profile, name, comm, exe, arch, syscall, success, exit, a0-a3, items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid, key, proctitle).
7. The `msg='...'` field is stored as-is in the `msg` column (TEXT blob). It is NOT unpacked at staging. The msg blob contains key-value sub-fields (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) that will be unpacked during the 3NF transformation in iteration 2.
8. Set `source_host` to the YAML `host_key` for this host (= the directory name under `gather/`). Example: the file at `gather/intranet_server/logs/audit/audit.log` gets `source_host = 'intranet_server'`.
9. Set `source_log` to the log filename (e.g. `'audit.log'`).
10. Set `line_number` from the 1-based line position in the file.

**Provenance columns:**

| Column | Purpose | Example values |
|---|---|---|
| `source_host` | YAML host_key / directory name for the source host | "intranet_server", "internal_share" |
| `source_log` | Log filename | "audit.log" |
| `line_number` | 1-based line position in source file | 1..2316 (intranet), 1..732 (internal_share) |
| `raw_line` | Full original line text for auditability | The complete auditd log line |

`source_host` uses the YAML `host_key` verbatim (= the directory name under `gather/` and `labels/`). This is also the value in `stg_host_raw.host_key`, so the staging-to-3NF host_id lookup is a direct equality join: `source_host = stg_host_raw.host_key`. The same `source_host` values appear in `stg_attack_label_line_raw`, enabling direct equality joins between audit and label staging tables on `(source_host, source_log, line_number)`.

Candidate key: `(source_host, source_log, line_number)` - each line in a given source file is unique.

**Column schema (43 columns):**

| # | Column | Type | Nullable | Source | Notes |
|---|---|---|---|---|---|
| 1 | row_id | SERIAL | PK | (generated) | Surrogate key |
| 2 | source_host | VARCHAR(30) | NOT NULL | (derived from path) | Provenance |
| 3 | source_log | VARCHAR(50) | NOT NULL | (derived from path) | Provenance |
| 4 | line_number | INTEGER | NOT NULL | (line position) | Provenance |
| 5 | raw_line | TEXT | NOT NULL | (full line) | Provenance |
| 6 | type | VARCHAR(20) | NOT NULL | type= | Event type discriminator (15 distinct) |
| 7 | epoch | DOUBLE PRECISION | NOT NULL | audit(...:...) | Unix timestamp with ms precision |
| 8 | serial | INTEGER | NOT NULL | audit(...:...) | auditd serial number |
| 9 | timestamp | TIMESTAMPTZ | NOT NULL | (derived from epoch) | Human-readable timestamp |
| 10 | pid | INTEGER | nullable | pid= | Process ID |
| 11 | uid | INTEGER | nullable | uid= | User ID |
| 12 | auid | BIGINT | nullable | auid= | Audit UID (4294967295 = unset sentinel) |
| 13 | ses | BIGINT | nullable | ses= | Session ID (4294967295 = unset sentinel) |
| 14 | msg | TEXT | nullable | msg='...' | Packed key-value blob (1NF violation, deferred). Non-null for ~85% of rows (PAM, SERVICE types). |
| 15 | old_auid | BIGINT | nullable | old-auid= | LOGIN events only |
| 16 | old_ses | BIGINT | nullable | old-ses= | LOGIN events only |
| 17 | tty | VARCHAR(30) | nullable | tty= | LOGIN, USER_LOGIN, SYSCALL |
| 18 | res | VARCHAR(10) | nullable | res= | LOGIN top-level result ("1" = success) |
| 19 | apparmor | VARCHAR(20) | nullable | apparmor= | AVC events only |
| 20 | operation | VARCHAR(30) | nullable | operation= | AVC events only |
| 21 | info | TEXT | nullable | info= | AVC events only |
| 22 | profile | VARCHAR(50) | nullable | profile= | AVC events only |
| 23 | name | TEXT | nullable | name= | AVC events only |
| 24 | comm | VARCHAR(50) | nullable | comm= | AVC, SYSCALL events |
| 25 | exe | TEXT | nullable | exe= | SYSCALL events (top-level) |
| 26 | arch | VARCHAR(20) | nullable | arch= | SYSCALL events only |
| 27 | syscall | INTEGER | nullable | syscall= | SYSCALL events only |
| 28 | success | VARCHAR(5) | nullable | success= | SYSCALL events only |
| 29 | exit | BIGINT | nullable | exit= | SYSCALL events only |
| 30 | a0 | VARCHAR(20) | nullable | a0= | SYSCALL register args |
| 31 | a1 | VARCHAR(20) | nullable | a1= | SYSCALL register args |
| 32 | a2 | VARCHAR(20) | nullable | a2= | SYSCALL register args |
| 33 | a3 | VARCHAR(20) | nullable | a3= | SYSCALL register args |
| 34 | items | INTEGER | nullable | items= | SYSCALL item count |
| 35 | ppid | INTEGER | nullable | ppid= | SYSCALL parent PID |
| 36 | gid | INTEGER | nullable | gid= | SYSCALL group ID |
| 37 | euid | INTEGER | nullable | euid= | SYSCALL effective UID |
| 38 | suid | INTEGER | nullable | suid= | SYSCALL saved UID |
| 39 | fsuid | INTEGER | nullable | fsuid= | SYSCALL filesystem UID |
| 40 | egid | INTEGER | nullable | egid= | SYSCALL effective GID |
| 41 | sgid | INTEGER | nullable | sgid= | SYSCALL saved GID |
| 42 | fsgid | INTEGER | nullable | fsgid= | SYSCALL filesystem GID |
| 43 | key | VARCHAR(20) | nullable | key= | SYSCALL audit key |
| 44 | proctitle | TEXT | nullable | proctitle= | PROCTITLE hex-encoded command line |

Note: Column numbering goes to 44 because row_id is #1 and proctitle is the last. The table has 43 non-PK columns + 1 PK = 44 total. (The findings docs reference "43 columns" counting from source_host onward, excluding row_id.)

**DDL:**

```sql
CREATE TABLE stg_audit_line_raw (
    row_id          SERIAL PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,
    source_log      VARCHAR(50) NOT NULL,
    line_number     INTEGER NOT NULL,
    raw_line        TEXT NOT NULL,
    type            VARCHAR(20) NOT NULL,
    epoch           DOUBLE PRECISION NOT NULL,
    serial          INTEGER NOT NULL,
    timestamp       TIMESTAMP WITH TIME ZONE NOT NULL,
    pid             INTEGER,
    uid             INTEGER,
    auid            BIGINT,
    ses             BIGINT,
    msg             TEXT,
    old_auid        BIGINT,
    old_ses         BIGINT,
    tty             VARCHAR(30),
    res             VARCHAR(10),
    apparmor        VARCHAR(20),
    operation       VARCHAR(30),
    info            TEXT,
    profile         VARCHAR(50),
    name            TEXT,
    comm            VARCHAR(50),
    exe             TEXT,
    arch            VARCHAR(20),
    syscall         INTEGER,
    success         VARCHAR(5),
    exit            BIGINT,
    a0              VARCHAR(20),
    a1              VARCHAR(20),
    a2              VARCHAR(20),
    a3              VARCHAR(20),
    items           INTEGER,
    ppid            INTEGER,
    gid             INTEGER,
    euid            INTEGER,
    suid            INTEGER,
    fsuid           INTEGER,
    egid            INTEGER,
    sgid            INTEGER,
    fsgid           INTEGER,
    key             VARCHAR(20),
    proctitle       TEXT
);
```

### Loading: Both Audit Sources into stg_audit_line_raw

Both audit.log files load into the same staging table. The process is identical per file, differing only in the `source_host` value.

**Loading procedure:**

```
1. Parse intranet_server/logs/audit/audit.log:
   - Set source_host = 'intranet_server'
   - Set source_log  = 'audit.log'
   - For each line: parse fields, set line_number, store raw_line
   - Insert 2,316 rows

2. Parse internal_share/logs/audit/audit.log:
   - Set source_host = 'internal_share'
   - Set source_log  = 'audit.log'
   - For each line: parse fields, set line_number, store raw_line
   - Insert 732 rows
```

**Verification after loading:**

```sql
-- Total rows
SELECT COUNT(*) FROM stg_audit_line_raw;
-- Expected: 3,048

-- Per source host
SELECT source_host, COUNT(*)
FROM stg_audit_line_raw
GROUP BY source_host;
-- Expected: intranet_server = 2,316; internal_share = 732

-- Candidate key uniqueness
SELECT source_host, source_log, line_number, COUNT(*)
FROM stg_audit_line_raw
GROUP BY source_host, source_log, line_number
HAVING COUNT(*) > 1;
-- Expected: 0 rows (no duplicates)
```

### Per-Source Differences

| Aspect | intranet_server (Notebook 05) | internal_share (Notebook 07) |
|---|---|---|
| Rows | 2,316 | 732 |
| Event types | 15 | 11 (missing USER_LOGIN, USER_AUTH, USER_CMD, CRED_REFR) |
| Attack type | Privilege escalation (su, sudo) | Data exfiltration (dnsteal service) |
| Labeled lines | 9 (lines 1860-1868) | 2 (lines 667-668) |
| uid values | 0 (root), 33 (www-data), 1002 (jhall) | 0 (root) only |
| Network context | Attacker IP 172.19.131.174 visible in msg | No real IPs (all hostname=?, addr=?) |
| msg non-null rows | ~86% | ~84% |

### Event Type Distribution (Combined)

| Event type | Intranet | Internal share | Total | Category |
|---|---|---|---|---|
| USER_ACCT | 305 | 106 | 411 | PAM |
| CRED_ACQ | 308 | 106 | 414 | PAM |
| USER_START | 306 | 106 | 412 | PAM |
| USER_END | 302 | 106 | 408 | PAM |
| CRED_DISP | 302 | 106 | 408 | PAM |
| USER_AUTH | 1 | 0 | 1 | PAM |
| CRED_REFR | 1 | 0 | 1 | PAM |
| USER_LOGIN | 3 | 0 | 3 | PAM |
| USER_CMD | 1 | 0 | 1 | PAM |
| LOGIN | 304 | 106 | 410 | Login |
| SERVICE_START | 241 | 47 | 288 | Service |
| SERVICE_STOP | 230 | 37 | 267 | Service |
| AVC | 4 | 4 | 8 | Kernel |
| SYSCALL | 4 | 4 | 8 | Kernel |
| PROCTITLE | 4 | 4 | 8 | Kernel |
| **Total** | **2,316** | **732** | **3,048** | |

### msg Blob: What It Contains (Staging Stores As-Is)

The `msg` column stores the full `msg='...'` string as a TEXT blob in staging. It is not parsed at the staging layer. For reference, these are the sub-fields packed inside, relevant for the 3NF iteration:

**PAM events** (USER_ACCT, CRED_ACQ, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR, USER_LOGIN):
- Sub-fields: `op`, `acct`, `exe`, `hostname`, `addr`, `terminal`, `res`

**USER_CMD events** (1 event in intranet, 0 in internal_share):
- Sub-fields: `cmd` (hex-encoded), `cwd`, `terminal`, `id`

**SERVICE events** (SERVICE_START, SERVICE_STOP):
- Sub-fields: `unit`, `comm`, `exe`, `hostname`, `addr`, `terminal`, `res`

**Other types** (LOGIN, AVC, SYSCALL, PROCTITLE):
- `msg` is NULL. Their fields are already top-level columns.

### Known Normalization Violations (for iteration 2)

- **1NF:** `msg` TEXT column packs 5-12 key-value pairs into a single blob for PAM and SERVICE events (~85% of rows). Normalization should unpack into separate columns on appropriate subtype tables.
- **3NF:** `type -> populated field set`. The event type transitively determines which columns are non-NULL. This motivates subtype modeling (disjoint specialization) in the 3NF schema.

### Sentinel Value Note

`auid = 4294967295` and `ses = 4294967295` appear in ~45% of audit events. This is the Linux kernel's "unset" sentinel (0xFFFFFFFF), meaning the process has no associated login session (e.g., cron jobs, systemd services). Stored as-is at staging. Handling (convert to NULL vs. keep) will be decided in iteration 2.

### Dual Result Field Note

Two different `res` fields exist in the raw data:
- **PAM/SERVICE events:** `res` is inside the `msg` blob, always text "success". Not visible at staging (packed in msg).
- **LOGIN events:** `res` is a top-level column, value "1" (numeric string meaning success). Visible at staging.

These are semantically the same (operation result) but have different formats. Unification will be addressed in iteration 2.

---

## Source Family 3: Attack Labels (Notebook 09)

### Source Files

8 JSONL files across 5 hosts, all sharing an identical JSON schema. All 8 files merge into a single staging table.

| # | Host | Log | Labeled lines | Line range | Raw log lines | Coverage |
|---|---|---|---|---|---|---|
| 1 | inet-firewall | dnsmasq.log | 54,035 | 1 - 254,393 | 275,900 | 19.6% |
| 2 | intranet_server | access.log.2 | 7,695 | 832 - 8,529 | 8,530 | 90.2% |
| 3 | intranet_server | error.log.2 | 36 | 1 - 36 | 36 | 100.0% |
| 4 | intranet_server | audit.log | 9 | 1,860 - 1,868 | 2,316 | 0.4% |
| 5 | intranet_server | auth.log | 8 | 145 - 152 | 272 | 2.9% |
| 6 | monitoring | cpu.log | 49 | 321 - 369 | 1,920 | 2.6% |
| 7 | vpn | openvpn.log | 28 | 4,331 - 4,358 | 5,537 | 0.5% |
| 8 | internal_share | audit.log | 2 | 667 - 668 | 732 | 0.3% |
| | **Total** | | **61,862** | | **295,243** | **21.0%** |

Source path pattern: `russellmitchell/labels/{host}/logs/{log_type}/{log_file}`

**Findings doc:** `docs/data_exploration/notebook_findings/naman_labels_findings.md`

**ER diagram:** `docs/er_diagrams/internal diagrams/attack_labels_er_v1_raw.drawio.xml`

### Staging Table: stg_attack_label_line_raw

The canonical name for this staging table is `stg_attack_label_line_raw`. All 8 JSONL files merge into this single table.

**Row-level grain:** One row per labeled line in a source log file. 61,862 rows total.

**Parsing logic:**

Each JSONL file contains one JSON object per line with 3 fields:
- `line` (int): line number in the corresponding raw log file
- `labels` (list of str): attack phase tags (2-4 per record)
- `rules` (dict of str to list of str): detection rules that triggered each label

Parsing steps:
1. For each of the 8 JSONL files, derive `source_host` and `source_log` from the file path.
2. Read each JSON line and extract the 3 fields.
3. Store `labels` as a JSON-serialized TEXT string in `labels_json`.
4. Store `rules` as a JSON-serialized TEXT string in `rules_json`.
5. Map `line` to `line_number`.

**Provenance columns:**

| Column | Purpose | Why needed |
|---|---|---|
| `source_host` | YAML host_key / directory name for the source host | Derived from file path, not in JSONL data. Uses the same host_key values as `stg_audit_line_raw.source_host` and `stg_host_raw.host_key`. |
| `source_log` | Log filename the labels annotate | Derived from file path, not in JSONL data |
| `line_number` | Line number in the raw log being annotated | From JSONL `line` field |

Source provenance is required to distinguish identical line numbers across different files. For example, line 1 in `intranet_server/audit.log` is a different record from line 1 in `inet-firewall/dnsmasq.log`.

The `source_host` and `source_log` columns use the same values and widths (VARCHAR(30), VARCHAR(50)) as `stg_audit_line_raw`, enabling direct equality joins between the two staging tables on `(source_host, source_log, line_number)`.

Candidate key: `(source_host, source_log, line_number)` - verified unique across all 61,862 records.

**Column schema:**

| # | Column | Type | Nullable | Source | Notes |
|---|---|---|---|---|---|
| 1 | row_id | SERIAL | PK | (generated) | Surrogate key |
| 2 | source_host | VARCHAR(30) | NOT NULL | (derived from path) | Provenance; matches stg_audit_line_raw.source_host width |
| 3 | source_log | VARCHAR(50) | NOT NULL | (derived from path) | Provenance; matches stg_audit_line_raw.source_log width |
| 4 | line_number | INTEGER | NOT NULL | line | Line in the annotated raw log file |
| 5 | labels_json | TEXT | NOT NULL | labels | JSON array of 2-4 label strings |
| 6 | rules_json | TEXT | NOT NULL | rules | JSON dict mapping labels to rule arrays |

**DDL:**

```sql
CREATE TABLE stg_attack_label_line_raw (
    row_id          SERIAL PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,
    source_log      VARCHAR(50) NOT NULL,
    line_number     INTEGER NOT NULL,
    labels_json     TEXT NOT NULL,
    rules_json      TEXT NOT NULL,
    UNIQUE (source_host, source_log, line_number)
);
```

### Loading: All 8 JSONL Files into stg_attack_label_line_raw

**Loading procedure:**

```
For each of the 8 JSONL files:
  1. Derive source_host and source_log from the file path:
     - russellmitchell/labels/inet-firewall/logs/dns/dnsmasq.log
       -> source_host = 'inet-firewall', source_log = 'dnsmasq.log'
     - russellmitchell/labels/intranet_server/logs/audit/audit.log
       -> source_host = 'intranet_server', source_log = 'audit.log'
     - (and so on for all 8 files)

  2. For each JSON line in the file:
     - Parse the JSON object
     - INSERT INTO stg_attack_label_line_raw (
         source_host, source_log, line_number, labels_json, rules_json
       ) VALUES (
         derived_host, derived_log, obj.line,
         json_dumps(obj.labels), json_dumps(obj.rules)
       )
```

**Verification after loading:**

```sql
-- Total rows
SELECT COUNT(*) FROM stg_attack_label_line_raw;
-- Expected: 61,862

-- Per source file
SELECT source_host, source_log, COUNT(*)
FROM stg_attack_label_line_raw
GROUP BY source_host, source_log
ORDER BY COUNT(*) DESC;
-- Expected: inet-firewall/dnsmasq.log = 54,035 (largest), etc.

-- Candidate key uniqueness
SELECT source_host, source_log, line_number, COUNT(*)
FROM stg_attack_label_line_raw
GROUP BY source_host, source_log, line_number
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

### Relational Bridge to Other Staging Tables

The label data connects to raw log staging tables via the `(source_host, source_log, line_number)` tuple. For the two audit log files in scope:

- Labels for `intranet_server/audit.log` (9 rows, lines 1860-1868) join to `stg_audit_line_raw` rows where `source_host = 'intranet_server'` and `source_log = 'audit.log'`.
- Labels for `internal_share/audit.log` (2 rows, lines 667-668) join to `stg_audit_line_raw` rows where `source_host = 'internal_share'` and `source_log = 'audit.log'`.

The remaining 6 label files annotate log types not yet in scope (dnsmasq, access, error, auth, cpu, openvpn).

### Known Normalization Violations (for iteration 2)

- **1NF:** `labels_json` is a JSON array of 2-4 label strings per record. Should decompose into a junction table.
- **1NF:** `rules_json` is a nested JSON dict mapping labels to rule arrays. Should decompose into a junction table (one row per rule per label per record).
- **Structural constraint:** The `rules` dict keys always match the `labels` array entries (0 mismatches across 61,862 records). The decomposed schema should preserve this via foreign keys.
- **External FD:** `label_name -> attack_phase` (22 labels map to 7 phases, from project taxonomy). Relevant for a 3NF lookup table but not present in the JSONL data itself.

---

## Staging Loading Order

Staging tables have one FK dependency: `stg_host_log_config_raw` references `stg_host_raw`. The other two staging tables have no FK dependencies at the staging layer.

```
Phase 1 (parallel, no dependencies):
  - stg_host_raw              (22 rows from servers.yaml)
  - stg_audit_line_raw         (3,048 rows from 2 audit.log files)
  - stg_attack_label_line_raw  (61,862 rows from 8 JSONL files)

Phase 2 (after stg_host_raw):
  - stg_host_log_config_raw    (66 rows, FK -> stg_host_raw)
```

In practice, loading `stg_host_raw` first and then everything else is simplest.

---

## 3NF Transformation: Host Inventory (Iteration 2)

Source staging tables: `stg_host_raw` (22 rows, 15 cols), `stg_host_log_config_raw` (66 rows, 7 cols).
Target: 7 normalized tables in the host domain.
Findings doc: `docs/data_exploration/notebook_findings/naman_hosts_findings.md`.
EER diagram: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.

**Implementation note:** 1NF and 2NF are documented below as logical normalization stages for audit and teaching purposes. They are not separate physical schemas. The DAT-59 implementation should create only the final 3NF physical tables and write ETL that transforms directly from staging to 3NF.

### Row Grain Recap

| Staging table | Row grain | Rows | PK | Natural key(s) |
|---|---|---|---|---|
| `stg_host_raw` | One row per host machine | 22 | `host_id` (SERIAL) | `host_key` (UNIQUE), `hostname` (UNIQUE) |
| `stg_host_log_config_raw` | One row per log config per host | 66 | `config_id` (SERIAL) | `(host_id, log_path)`-candidate business key, verified unique in current data |

### Functional Dependencies

Identified from data and business rules (see findings doc, section 2).

| FD | Determinant | Dependent(s) | Type | Action |
|---|---|---|---|---|
| FD1 | `host_key` | all other attributes | Candidate key | None (key) |
| FD2 | `hostname` | all other attributes | Candidate key | None (key) |
| FD3 | `default_ipv4_address` | `hostname` | Observed, not confirmed | Ignore (not a reliable business rule) |
| FD4 | `openvpn_user` | `username` | Observed in 3 hosts | Ignore (coincidental in testbed) |
| FD5 | `distribution_release` | `distribution`, `distribution_version` | **Transitive dependency** | **Resolve at 3NF** (extract lookup table) |

### Normalization Violations in Staging

| Violation | Table | Field(s) | Normal form | Resolution |
|---|---|---|---|---|
| Multi-valued JSON array | `stg_host_raw` | `groups` (2-5 values, 17 distinct) | 1NF | Junction table `host_group` |
| Multi-valued JSON array | `stg_host_raw` | `fqdns` (0-4 values) | 1NF | Child table `host_fqdn` |
| Multi-valued JSON array | `stg_host_raw` | `ipv4_addresses` (1-3 values) | 1NF | Child table `host_ipv4` |
| Multi-valued JSON array | `stg_host_raw` | `ipv6_addresses` (1-3 values) | 1NF | Child table `host_ipv6` |
| JSON blob (key-value pairs) | `stg_host_log_config_raw` | `add_field_json` (4 distinct keys) | 1NF (minor) | **Practical exception:** retained as opaque JSON payload (see design decisions) |
| Transitive dependency | `stg_host_raw` | `distribution_release -> distribution, distribution_version` | 3NF | Lookup table `os_release` |

### Logical Stage 1: 1NF-Resolve Multi-Valued Attributes

Explode 4 JSON array columns from `stg_host_raw` into separate tables. Drop those columns from the host table.

**host (at 1NF)**-22 rows, multi-valued columns removed:

| Column | Type | Nullable | Change from staging |
|---|---|---|---|
| host_id | SERIAL | PK | Unchanged |
| host_key | VARCHAR(50) | UNIQUE, NOT NULL | Unchanged |
| hostname | VARCHAR(100) | UNIQUE, NOT NULL | Unchanged |
| username | VARCHAR(50) | nullable | Unchanged |
| openvpn_user | VARCHAR(50) | nullable | Unchanged |
| distribution | VARCHAR(50) | NOT NULL | Unchanged (moves at 3NF) |
| distribution_release | VARCHAR(20) | NOT NULL | Unchanged (moves at 3NF) |
| distribution_version | VARCHAR(20) | NOT NULL | Unchanged (moves at 3NF) |
| default_ipv4_address | VARCHAR(45) | NOT NULL | Unchanged |
| default_ipv6_address | VARCHAR(45) | NOT NULL | Unchanged |
| timezone | VARCHAR(10) | NOT NULL | Unchanged |

Dropped: `groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses`.

New junction/child tables created:
- `host_group(host_id PK, group_name PK)`-63 rows, M:N junction
- `host_fqdn(host_id PK, fqdn PK)`-20 rows, 1:N child
- `host_ipv4(host_id PK, ipv4_address PK)`-24 rows, 1:N child
- `host_ipv6(host_id PK, ipv6_address PK)`-24 rows, 1:N child

### Logical Stage 2: Composite Key Identification + 2NF Check

After 1NF, composite keys exist only in junction/child tables:

| Table | PK | PK type | Non-key attributes |
|---|---|---|---|
| host | `host_id` | Single-column | 10 |
| host_group | `(host_id, group_name)` | Composite | 0 (all-key) |
| host_fqdn | `(host_id, fqdn)` | Composite | 0 (all-key) |
| host_ipv4 | `(host_id, ipv4_address)` | Composite | 0 (all-key) |
| host_ipv6 | `(host_id, ipv6_address)` | Composite | 0 (all-key) |
| host_log_config | `config_id` | Single-column | 5 |

**2NF result: no partial dependencies exist.** Entity tables have single-column PKs (partial deps impossible). Junction tables are all-key (no non-key attributes to be partially dependent). No schema changes at 2NF.

### Logical Stage 3: 3NF-Resolve Transitive Dependencies

FD5 creates a transitive dependency in the host table:

```
host_key -> distribution_release -> distribution, distribution_version
```

`distribution_release` is a non-key attribute that determines two other non-key attributes (`bionic` always means Ubuntu 18.04; `stretch` always means Debian 9.11).

**Resolution:** Extract an `os_release` lookup table. Replace the 3 distribution columns on host with an `os_release_id` FK.

All other tables pass 3NF. `host_log_config` has no transitive dependencies (`log_type` does not determine `codec` or `file_chunk_size`).

---

### Final 3NF Tables: Host Domain

7 tables total. These are the physical tables for DAT-59 implementation.

#### os_release (2 rows)

3NF lookup table. Resolves transitive dependency `distribution_release -> distribution, distribution_version`. Row grain: one row per OS release.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| os_release_id | SERIAL | PK | Surrogate key |
| distribution_release | VARCHAR(20) | UNIQUE, NOT NULL | Natural key; determinant from FD5 |
| distribution | VARCHAR(50) | NOT NULL | "Ubuntu" or "Debian" |
| distribution_version | VARCHAR(20) | NOT NULL | "18.04" or "9.11" |

```sql
CREATE TABLE os_release (
    os_release_id        SERIAL PRIMARY KEY,
    distribution_release VARCHAR(20) NOT NULL UNIQUE,
    distribution         VARCHAR(50) NOT NULL,
    distribution_version VARCHAR(20) NOT NULL
);
```

**ETL:** `SELECT DISTINCT distribution_release, distribution, distribution_version FROM stg_host_raw` -> insert 2 rows.

#### host (22 rows)

Central reference entity. Every machine in the AIT testbed. Row grain: one row per host.

`host_key` is the downstream integration key: it aligns with `stg_audit_line_raw.source_host` and `stg_attack_label_line_raw.source_host`, enabling FK resolution when loading audit events and labels into 3NF via `host.host_key = source_host`.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| host_id | SERIAL | PK | Surrogate key |
| host_key | VARCHAR(50) | UNIQUE, NOT NULL | YAML dict key (e.g. "intranet_server"); integration key for cross-domain FK resolution |
| hostname | VARCHAR(100) | UNIQUE, NOT NULL | Machine hostname |
| username | VARCHAR(50) | nullable | Only 7 employee hosts |
| openvpn_user | VARCHAR(50) | nullable | Only 3 remote employees |
| default_ipv4_address | VARCHAR(45) | NOT NULL | Single-valued; always 1 per host |
| default_ipv6_address | VARCHAR(45) | NOT NULL | Single-valued; always 1 per host |
| timezone | VARCHAR(10) | NOT NULL | "UTC" for all 22 hosts (retained as source data) |
| os_release_id | INT | FK -> os_release, NOT NULL | 3NF lookup reference |

```sql
CREATE TABLE host (
    host_id              SERIAL PRIMARY KEY,
    host_key             VARCHAR(50) NOT NULL UNIQUE,
    hostname             VARCHAR(100) NOT NULL UNIQUE,
    username             VARCHAR(50),
    openvpn_user         VARCHAR(50),
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    timezone             VARCHAR(10) NOT NULL,
    os_release_id        INT NOT NULL REFERENCES os_release(os_release_id)
);
```

**ETL:** Read from `stg_host_raw`. For each row, look up `distribution_release` in `os_release` to get `os_release_id`. Drop `distribution`, `distribution_release`, `distribution_version`.

#### host_group (63 rows)

1NF resolution of multi-valued `groups` field. M:N junction (a host belongs to 2-5 groups; a group contains 1-10 hosts). Row grain: one row per group membership per host.

| Column | Type | Constraint |
|---|---|---|
| host_id | INT | PK, FK -> host |
| group_name | VARCHAR(50) | PK |

```sql
CREATE TABLE host_group (
    host_id    INT NOT NULL REFERENCES host(host_id),
    group_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (host_id, group_name)
);
```

**ETL:** For each row in `stg_host_raw`, `json.loads(groups)` produces a list. Insert one row per element with the host's `host_id`.

17 distinct group names: attacker, beatservers, dmz, dnat, dnsservers, employee, ext_mail, ext_user, firewall, internal_employee, internet, intranet, mailserver, proxied, remote_employee, servers, share.

#### host_fqdn (20 rows)

1NF resolution of multi-valued `fqdns` field. 1:N child (each FQDN belongs to exactly one host). Row grain: one row per FQDN per host.

| Column | Type | Constraint |
|---|---|---|
| host_id | INT | PK, FK -> host |
| fqdn | VARCHAR(255) | PK |

```sql
CREATE TABLE host_fqdn (
    host_id INT NOT NULL REFERENCES host(host_id),
    fqdn    VARCHAR(255) NOT NULL,
    PRIMARY KEY (host_id, fqdn)
);
```

**ETL:** For each row in `stg_host_raw` where `fqdns IS NOT NULL`, `json.loads(fqdns)` produces a list. Insert one row per element. 7 hosts with NULL fqdns produce zero rows. Per-host: 12 hosts have 1, 2 hosts have 2, 1 host has 4.

#### host_ipv4 (24 rows)

1NF resolution of multi-valued `ipv4_addresses` field. 1:N child. Row grain: one row per IPv4 address per host.

| Column | Type | Constraint |
|---|---|---|
| host_id | INT | PK, FK -> host |
| ipv4_address | VARCHAR(45) | PK |

```sql
CREATE TABLE host_ipv4 (
    host_id      INT NOT NULL REFERENCES host(host_id),
    ipv4_address VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv4_address)
);
```

**ETL:** For each row in `stg_host_raw`, `json.loads(ipv4_addresses)` produces a list. Insert one row per element. 21 hosts have 1 address; inet-firewall has 3 (172.19.128.1, 192.168.230.4, 10.143.0.1).

**Validation rule:** `host.default_ipv4_address` must exist in `host_ipv4.ipv4_address` for the same `host_id`. ETL must verify this after loading (see verification queries).

#### host_ipv6 (24 rows)

1NF resolution of multi-valued `ipv6_addresses` field. 1:N child. Row grain: one row per IPv6 address per host.

| Column | Type | Constraint |
|---|---|---|
| host_id | INT | PK, FK -> host |
| ipv6_address | VARCHAR(45) | PK |

```sql
CREATE TABLE host_ipv6 (
    host_id      INT NOT NULL REFERENCES host(host_id),
    ipv6_address VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv6_address)
);
```

**ETL:** Same pattern as host_ipv4. 21 hosts have 1; inet-firewall has 3.

**Validation rule:** `host.default_ipv6_address` must exist in `host_ipv6.ipv6_address` for the same `host_id`.

#### host_log_config (66 rows)

Child entity for per-host log collection configuration. Weak entity in EER terms, identified by `(host_id, log_path)` (candidate business key, verified unique in current data-should be enforced with a UNIQUE constraint). Row grain: one row per log config per host.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| config_id | SERIAL | PK | Surrogate key |
| host_id | INT | FK -> host, NOT NULL | |
| log_path | TEXT | NOT NULL | e.g. "/var/log/audit/audit.log" |
| log_type | VARCHAR(50) | NOT NULL | 11 distinct log types |
| codec | TEXT | nullable | String or JSON-serialized dict |
| file_chunk_size | INT | nullable | |
| add_field_json | TEXT | nullable | **Practical exception:** opaque JSON payload retained as-is (see design decisions) |

```sql
CREATE TABLE host_log_config (
    config_id       SERIAL PRIMARY KEY,
    host_id         INT NOT NULL REFERENCES host(host_id),
    log_path        TEXT NOT NULL,
    log_type        VARCHAR(50) NOT NULL,
    codec           TEXT,
    file_chunk_size INT,
    add_field_json  TEXT,
    UNIQUE (host_id, log_path)
);
```

**ETL:** `stg_host_log_config_raw` contains only the staging surrogate `host_id`, not `host_key`. To resolve the final `host.host_id` FK:
1. Join `stg_host_log_config_raw` to `stg_host_raw` on `stg_host_log_config_raw.host_id = stg_host_raw.host_id` to recover `host_key`.
2. Join to final `host` on `host.host_key = stg_host_raw.host_key` to get the final `host.host_id`.
3. Insert into `host_log_config` using the final `host.host_id`, copying `log_path`, `log_type`, `codec`, `file_chunk_size`, `add_field_json` directly.

11 distinct log types: apache_access, apache_error, audit, auth, dnsmasq, dnsteal, kyoushi, metricsbeat, openvpn, pcap, syslog.

`add_field_json` contains up to 4 metadata keys: `[@metadata][kyoushi][sm]` (string), `[@metadata][kyoushi][httpd_dirs]` (array), `[@metadata][pipeline]` (string), `[@metadata][host_override]` (boolean).

### Resolved Design Decisions

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| 1 | Combine `host_ipv4` + `host_ipv6`? | Keep separate | Different formats/semantics; never compared in analysis |
| 2 | Decompose `add_field_json`? | **Retain as opaque JSON payload** | Deliberate practical exception. Only 4 keys; config-level metadata not queried in analysis. Strictly speaking a 1NF violation, but decomposing adds a table for negligible analytical value. Scoped out of DAT-59. |
| 3 | Drop `timezone`? | Keep | Real source data; constant "UTC" but dropping constants is optimization, not normalization |
| 4 | Redundancy: `default_ipv4/ipv6` on host vs. child tables? | Keep both; enforce with ETL validation | Default is a scalar property of the host; child tables list all addresses. ETL verifies `default_ipv4_address` exists in `host_ipv4` for the same host (see verification queries) |
| 5 | `host_group` as all-key junction vs. separate `group` entity? | All-key junction | 17 stable groups with no attributes of their own |
| 6 | FD4 (`openvpn_user -> username`)? | Ignore for now | Coincidental in 3 hosts; not a business rule. May revisit when VPN log normalization (openvpn.log) is in scope |
| 7 | Rename `distribution` table? | Named `os_release` | Row grain is one row per OS release; avoids confusion with `distribution` column name |

### 3NF Loading Order: Host Domain

```
Phase 1: os_release                (2 rows, no FK deps)
Phase 2: host                      (22 rows, FK -> os_release)
Phase 3: host_group                (63 rows, FK -> host)
         host_fqdn                 (20 rows, FK -> host)
         host_ipv4                 (24 rows, FK -> host)
         host_ipv6                 (24 rows, FK -> host)
         host_log_config           (66 rows, FK -> host)
         (all 5 independent, can load in parallel)
```

### Verification Queries: Host Domain

```sql
-- Row counts (exact expected values for ETL verification)
SELECT 'os_release' AS tbl, COUNT(*) AS actual, 2 AS expected FROM os_release
UNION ALL SELECT 'host', COUNT(*), 22 FROM host
UNION ALL SELECT 'host_group', COUNT(*), 63 FROM host_group
UNION ALL SELECT 'host_fqdn', COUNT(*), 20 FROM host_fqdn
UNION ALL SELECT 'host_ipv4', COUNT(*), 24 FROM host_ipv4
UNION ALL SELECT 'host_ipv6', COUNT(*), 24 FROM host_ipv6
UNION ALL SELECT 'host_log_config', COUNT(*), 66 FROM host_log_config;

-- os_release lookup correctness
SELECT * FROM os_release;
-- Expected: (bionic, Ubuntu, 18.04), (stretch, Debian, 9.11)

-- Every host has a valid os_release_id
SELECT h.host_id, h.host_key
FROM host h
LEFT JOIN os_release r ON h.os_release_id = r.os_release_id
WHERE r.os_release_id IS NULL;
-- Expected: 0 rows

-- Groups per host (should be 2-5)
SELECT h.host_key, COUNT(*) AS group_count
FROM host h
JOIN host_group hg ON h.host_id = hg.host_id
GROUP BY h.host_key
ORDER BY group_count;
-- Expected: min 2, max 5, total 63

-- default_ipv4 must exist in host_ipv4 for same host (ETL validation rule)
SELECT h.host_key, h.default_ipv4_address
FROM host h
WHERE NOT EXISTS (
    SELECT 1 FROM host_ipv4 ip
    WHERE ip.host_id = h.host_id
      AND ip.ipv4_address = h.default_ipv4_address
);
-- Expected: 0 rows (every default must be in the child table)

-- default_ipv6 must exist in host_ipv6 for same host (ETL validation rule)
SELECT h.host_key, h.default_ipv6_address
FROM host h
WHERE NOT EXISTS (
    SELECT 1 FROM host_ipv6 ip
    WHERE ip.host_id = h.host_id
      AND ip.ipv6_address = h.default_ipv6_address
);
-- Expected: 0 rows

-- Log configs per host (should be 1-9)
SELECT h.host_key, COUNT(*) AS config_count
FROM host h
JOIN host_log_config lc ON h.host_id = lc.host_id
GROUP BY h.host_key
ORDER BY config_count;
-- Expected: min 1, max 9, total 66

-- Candidate business key uniqueness for host_log_config
SELECT host_id, log_path, COUNT(*)
FROM host_log_config
GROUP BY host_id, log_path
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

---

## 3NF Transformation: Audit Events

Source staging table: `stg_audit_line_raw` (3,048 rows, 44 cols).
Target: 10 normalized tables in the audit domain.
Findings docs: `docs/data_exploration/notebook_findings/naman_audit_intranet_findings.md`, `naman_audit_internal_share_findings.md`.
EER diagram: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.
Reference: DATA201 Lecture 4 (normalization definitions).

Implementation note: 1NF and 2NF are documented below as logical normalization stages for audit and teaching purposes. They are not separate physical schemas. The implementation creates only the final 3NF physical tables and writes ETL that transforms directly from staging to 3NF.

### Row Grain Recap

| Staging table | Row grain | Rows | PK | Natural key(s) |
|---|---|---|---|---|
| `stg_audit_line_raw` | One row per line in a source audit.log file | 3,048 | `row_id` (SERIAL) | `(source_host, source_log, line_number)` verified unique |

### Normalization Issues (Audit vs. Lecture 4)

| NF | Issue in staging | Lecture 4 view | Resolution |
|---|---|---|---|
| 1NF | `msg` holds multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) in one cell. Non-atomic value / repeating group. | Not 1NF: one cell does not hold a single value. | Unpack into atomic attributes in a separate `audit_message` table (0..1 per audit event). Each attribute is one column, one value per row. |
| 2NF | Staging uses surrogate `row_id`; natural candidate key is `(source_host, source_log, line_number)` or `(host_id, line_number)`. Attributes like `type`, `epoch`, `pid` depend on the whole key. | With composite key, no non-key attribute may depend on only part of the key. | 3NF schema uses `(host_id, line_number)` as business key; `audit_event` has no partial dependency (all non-keys depend on event_id / whole key). Subtypes use `event_id` as sole key; no composite key, so 2NF holds. |
| 3NF | Event `type` determines which other columns are populated (e.g. LOGIN populates old_auid, old_ses, tty, res; SYSCALL populates syscall, arch, success, tty, ...). Non-key attributes effectively depend on another non-key (type). | Transitive dependency: Key -> type -> field set. Non-key depending on non-key. | Split into subtype tables: each subtype table's non-key attributes depend only on `event_id` (the key). Type is stored once in `audit_event`; type-specific attributes live in the subtype that corresponds to that type, so there is no non-key -> non-key dependency in a single table. |

Anomalies avoided: update (change msg content in one row of audit_message); insert (add event without forcing duplicate msg columns across subtypes); delete (delete an event does not leave orphaned msg attributes in a mixed table).

### Logical Stage 1: 1NF Resolution

The `msg` TEXT blob in staging packs 5 to 12 key-value pairs into a single cell for PAM and SERVICE events (~85% of rows). 1NF requires every column to hold a single atomic value.

Resolution: Create `audit_message` as a separate table (0..1 per event) that stores each msg sub-field as its own column: op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd.

Events with non-null msg in staging: 2,614 rows. Events with null msg (LOGIN, AVC, SYSCALL, PROCTITLE): 434 rows. These do not get audit_message rows.

### Logical Stage 2: 2NF Verification

After 1NF, the design uses `event_id` (single-column surrogate) as PK on `audit_event` and `audit_message`. Subtypes also use `event_id` as their sole PK. No composite keys with non-key attributes exist.

2NF result: no partial dependencies. This is a verification checkpoint, not a schema change.

### Logical Stage 3: 3NF Resolution via Subtype Tables

The event `type` column creates a transitive-like dependency: `event_id -> type -> populated field set`. Different event types populate entirely different sets of columns, meaning non-key attributes depend on another non-key (`type`).

Resolution: Split into 8 subtype tables (total, disjoint specialization). Each subtype holds only the columns relevant to its event type(s), and those columns depend only on `event_id`. The `type` column remains on `audit_event` as the discriminator.

Specialization constraint (total, disjoint): All 15 event types in the current data map to exactly one of the 8 subtypes, so every `audit_event` row is routed to exactly one subtype table (total). No event belongs to more than one subtype (disjoint). The implementation loader enforces this: route every row, raise an error on unrecognized types.

EER divergence note: The current EER (`combined_eer_3nf_v1.drawio.xml`) annotates the audit subtype specialization as "partial, disjoint." The data validates total coverage, so this document and the implementation use "total, disjoint." EER reconciliation is deferred.

### Business Key: `(host_id, line_number)`

The staging candidate key is `(source_host, source_log, line_number)`. The 3NF design simplifies this to `(host_id, line_number)` because:

1. `source_log` is always `'audit.log'` for all audit rows (only one distinct value in staging).
2. Each host has exactly one audit.log file in the dataset.
3. `host_id` is a 1:1 lookup from `source_host` via `host.host_key`.

Validated: 3,048 distinct `(host_id, line_number)` values out of 3,048 rows.

### Final 3NF Tables: Audit Domain

10 tables total: 1 supertype + 1 message table + 8 subtypes.

#### audit_event (3,048 rows)

Supertype table. One row per raw audit log line. Row grain: one row per audit event.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | SERIAL | PK | Surrogate key |
| host_id | INT | NOT NULL, FK -> host(host_id) | From `host.host_key = source_host` |
| line_number | INT | NOT NULL | Per-file line number |
| raw_line | TEXT | NOT NULL | Full line (provenance) |
| type | VARCHAR(20) | NOT NULL | Discriminator (15 values across both files) |
| epoch | DOUBLE PRECISION | NOT NULL | |
| serial | INT | NOT NULL | |
| timestamp | TIMESTAMPTZ | NOT NULL | |
| pid | INT | nullable | |
| uid | INT | nullable | |
| auid | BIGINT | nullable | 4294967295 = unset sentinel |
| ses | BIGINT | nullable | 4294967295 = unset sentinel |

Unique constraint: `(host_id, line_number)`.

```sql
CREATE TABLE audit_event (
    event_id    SERIAL PRIMARY KEY,
    host_id     INT NOT NULL REFERENCES host(host_id),
    line_number INT NOT NULL,
    raw_line    TEXT NOT NULL,
    type        VARCHAR(20) NOT NULL,
    epoch       DOUBLE PRECISION NOT NULL,
    serial      INT NOT NULL,
    timestamp   TIMESTAMP WITH TIME ZONE NOT NULL,
    pid         INT,
    uid         INT,
    auid        BIGINT,
    ses         BIGINT,
    UNIQUE (host_id, line_number)
);
```

ETL: For each row in `stg_audit_line_raw`, resolve `host_id` via `host.host_key = source_host`. Insert one row per staging row.

#### audit_message (2,614 rows)

1NF resolution table. Unpacks the `msg` TEXT blob into 12 atomic columns. Cardinality: 0..1 per audit_event (events with non-null msg in staging get one row here).

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) | 1:1 from event side, 0..1 from message side |
| op | VARCHAR(30) | nullable | PAM, USER_LOGIN |
| acct | VARCHAR(50) | nullable | PAM (e.g. "root", "jhall") |
| exe | TEXT | nullable | PAM, USER_LOGIN (e.g. "/usr/sbin/sshd") |
| hostname | VARCHAR(50) | nullable | PAM, USER_LOGIN (msg hostname, not host entity) |
| addr | VARCHAR(50) | nullable | PAM, USER_LOGIN |
| terminal | VARCHAR(30) | nullable | PAM, USER_LOGIN, USER_CMD (e.g. "cron", "/dev/pts/0") |
| res | VARCHAR(20) | nullable | PAM, USER_LOGIN, USER_CMD (e.g. "success") |
| unit | VARCHAR(100) | nullable | SERVICE (service name, e.g. "put", "apt-daily") |
| comm | VARCHAR(50) | nullable | SERVICE (e.g. "systemd") |
| id | INT | nullable | USER_LOGIN (e.g. 1002 = uid of jhall) |
| cwd | TEXT | nullable | USER_CMD (working directory) |
| cmd | TEXT | nullable | USER_CMD (hex-encoded command) |

```sql
CREATE TABLE audit_message (
    event_id INT PRIMARY KEY REFERENCES audit_event(event_id),
    op       VARCHAR(30),
    acct     VARCHAR(50),
    exe      TEXT,
    hostname VARCHAR(50),
    addr     VARCHAR(50),
    terminal VARCHAR(30),
    res      VARCHAR(20),
    unit     VARCHAR(100),
    comm     VARCHAR(50),
    id       INT,
    cwd      TEXT,
    cmd      TEXT
);
```

Which msg fields each event type populates (validated from staging):

| Event type | Populated msg fields |
|---|---|
| PAM (CRED_ACQ, USER_ACCT, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR) | op, acct, exe, hostname, addr, terminal, res |
| SERVICE (SERVICE_START, SERVICE_STOP) | unit, comm, exe, hostname, addr, terminal, res |
| USER_LOGIN | op, id, exe, hostname, addr, terminal, res |
| USER_CMD | cwd, cmd, terminal, res |

Note: `terminal` (in msg) and `tty` (top-level LOGIN/SYSCALL field) are different source fields with different semantics. `terminal` is a msg-embedded value (e.g. "/dev/pts/0", "cron"); `tty` is a top-level auditd field (e.g. "(none)", "pts1"). They are stored in separate tables and should not be conflated.

ETL: For each staging row where `msg` is not null, parse msg into the 12 attributes; insert one row with `event_id` from the audit_event insert.

#### Subtype Tables (8; total, disjoint)

Each subtype has `event_id` as PK and FK -> `audit_event(event_id)`. Exactly one subtype row per audit_event. Each table's only key is `event_id`; every non-key attribute depends only on `event_id` (no partial dependency, no transitive dependency).

**audit_pam_event** (2,055 rows: 1,525 intranet + 530 internal_share)

Event types: CRED_ACQ, USER_ACCT, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR.

| Column | Type | Constraint |
|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) |

Single-column key; no other attributes. Type-specific content lives in `audit_message` (join on event_id).

**audit_service_event** (555 rows: 471 intranet + 84 internal_share)

Event types: SERVICE_START, SERVICE_STOP.

| Column | Type | Constraint |
|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) |

Single-column key; no other attributes. Primary msg-derived attributes (unit, comm) are in `audit_message`.

**audit_user_login_event** (3 rows: all intranet_server)

Event types: USER_LOGIN.

| Column | Type | Constraint |
|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) |

Single-column key; no other attributes. Msg-derived attributes (terminal, id, exe, hostname, addr) are in `audit_message`.

**audit_user_cmd_event** (1 row: intranet_server only)

Event types: USER_CMD.

| Column | Type | Constraint |
|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) |

Single-column key; no other attributes. Msg-derived attributes (cwd, cmd, terminal, res) are in `audit_message`.

**audit_login_event** (410 rows: 304 intranet + 106 internal_share)

Event types: LOGIN. Attributes are top-level fields (msg is NULL for LOGIN).

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) | |
| old_auid | BIGINT | nullable | Often 4294967295 sentinel |
| old_ses | BIGINT | nullable | Often 4294967295 sentinel |
| tty | VARCHAR(30) | nullable | e.g. "(none)" |
| res | VARCHAR(10) | nullable | e.g. "1" (numeric success) |

```sql
CREATE TABLE audit_login_event (
    event_id INT PRIMARY KEY REFERENCES audit_event(event_id),
    old_auid BIGINT,
    old_ses  BIGINT,
    tty      VARCHAR(30),
    res      VARCHAR(10)
);
```

**audit_syscall_event** (8 rows: 4 intranet + 4 internal_share)

Event types: SYSCALL. Attributes are top-level fields (msg is NULL).

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) | |
| arch | VARCHAR(20) | nullable | e.g. x86_64 |
| syscall | INT | nullable | Syscall number |
| success | VARCHAR(5) | nullable | yes / no |
| exit | BIGINT | nullable | Exit code |
| exe | TEXT | nullable | Executable path |
| comm | VARCHAR(50) | nullable | Command name |
| tty | VARCHAR(30) | nullable | e.g. "pts1", "pts0" (all 8 rows non-null) |
| key | VARCHAR(20) | nullable | Audit key |

```sql
CREATE TABLE audit_syscall_event (
    event_id INT PRIMARY KEY REFERENCES audit_event(event_id),
    arch     VARCHAR(20),
    syscall  INT,
    success  VARCHAR(5),
    exit     BIGINT,
    exe      TEXT,
    comm     VARCHAR(50),
    tty      VARCHAR(30),
    key      VARCHAR(20)
);
```

Low-value columns (a0-a3, items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid) are omitted. They are present in staging but have negligible analytical value for 8 rows.

**audit_avc_event** (8 rows: 4 intranet + 4 internal_share)

Event types: AVC. Attributes are top-level fields (msg is NULL).

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) | |
| apparmor | VARCHAR(20) | nullable | AppArmor subsystem |
| operation | VARCHAR(30) | nullable | e.g. profile_replace |
| profile | VARCHAR(50) | nullable | Profile name |
| name | TEXT | nullable | Resource name |
| info | TEXT | nullable | Additional info |
| comm | VARCHAR(50) | nullable | e.g. "apparmor_parser" |

```sql
CREATE TABLE audit_avc_event (
    event_id  INT PRIMARY KEY REFERENCES audit_event(event_id),
    apparmor  VARCHAR(20),
    operation VARCHAR(30),
    profile   VARCHAR(50),
    name      TEXT,
    info      TEXT,
    comm      VARCHAR(50)
);
```

Note: `comm` appears in both `audit_syscall_event` and `audit_avc_event` because it is a top-level (outer) field shared by SYSCALL and AVC event types. These are distinct from the msg-embedded `comm` in `audit_message` (populated for SERVICE events). No collision occurs: SYSCALL/AVC have msg=NULL and do not get `audit_message` rows.

**audit_proctitle_event** (8 rows: 4 intranet + 4 internal_share)

Event types: PROCTITLE. Attributes are top-level fields (msg is NULL).

| Column | Type | Constraint | Notes |
|---|---|---|---|
| event_id | INT | PK, FK -> audit_event(event_id) | |
| proctitle | TEXT | nullable | Hex-encoded command line |

```sql
CREATE TABLE audit_proctitle_event (
    event_id  INT PRIMARY KEY REFERENCES audit_event(event_id),
    proctitle TEXT
);
```

#### Subtype Summary

| Subtype table | Key | Non-key columns | Msg fields (via audit_message join) | Row count |
|---|---|---|---|---|
| audit_pam_event | event_id | none | op, acct, exe, hostname, addr, terminal, res | 2,055 |
| audit_service_event | event_id | none | unit, comm, exe, hostname, addr, terminal, res | 555 |
| audit_user_login_event | event_id | none | op, id, exe, hostname, addr, terminal, res | 3 |
| audit_user_cmd_event | event_id | none | cwd, cmd, terminal, res | 1 |
| audit_login_event | event_id | old_auid, old_ses, tty, res | (msg is NULL for LOGIN) | 410 |
| audit_syscall_event | event_id | arch, syscall, success, exit, exe, comm, tty, key | (msg is NULL for SYSCALL) | 8 |
| audit_avc_event | event_id | apparmor, operation, profile, name, info, comm | (msg is NULL for AVC) | 8 |
| audit_proctitle_event | event_id | proctitle | (msg is NULL for PROCTITLE) | 8 |

Sum verified: 2,055 + 555 + 3 + 1 + 410 + 8 + 8 + 8 = 3,048.

#### Subtype Routing Map (for loader implementation)

| type value | Target subtype table |
|---|---|
| CRED_ACQ, USER_ACCT, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR | audit_pam_event |
| SERVICE_START, SERVICE_STOP | audit_service_event |
| USER_LOGIN | audit_user_login_event |
| USER_CMD | audit_user_cmd_event |
| LOGIN | audit_login_event |
| SYSCALL | audit_syscall_event |
| AVC | audit_avc_event |
| PROCTITLE | audit_proctitle_event |

### Resolved Design Decisions: Audit Domain

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| 1 | Subtype granularity | 8 subtypes (not 4) | Each distinct event-type family gets its own table. Avoids mixing PAM/USER_LOGIN/USER_CMD into one wide subtype with many nulls. |
| 2 | Shared audit_message table | One table for all msg-bearing subtypes | 12 unpacked msg attributes stored once; subtypes do not duplicate these columns. Join on event_id. |
| 3 | Sentinel values (auid/ses = 4294967295) | Stored as-is | Linux kernel "unset" sentinel preserved at staging and in 3NF. Handling (convert to NULL vs. keep) can be decided later. |
| 4 | Low-value syscall columns (a0-a3, items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid) | Omitted | Present in staging but negligible analytical value for 8 rows. Can be added if needed. |
| 5 | Business key simplification | `(host_id, line_number)` instead of full 3-column key | `source_log` is always 'audit.log'; each host has exactly one audit file in scope. |
| 6 | Result field unification (PAM msg res vs. LOGIN top-level res) | Kept separate | PAM/SERVICE res is text "success" in audit_message; LOGIN res is numeric "1" in audit_login_event. Different formats, different tables. |

### EER Divergences: Audit Domain

| Item | This document / implementation | Current EER | Deferred resolution |
|---|---|---|---|
| Audit subtype specialization | Total, disjoint (all 15 types routed) | Partial, disjoint | EER annotation should change to total |
| audit_syscall_event.tty | Included (all 8 rows non-null) | Not shown | Add to EER |
| audit_avc_event.comm | Included (all 8 rows non-null) | Not shown | Add to EER |
| audit_syscall_event.exit | Included | Not shown | Add to EER |
| audit_syscall_event.key | Included | Not shown | Add to EER |
| source_log in audit_event | Omitted (always "audit.log") | Present in Log Line superclass | Not needed for audit-only scope |

### 3NF Loading Order: Audit Domain

```
Phase 1: audit_event             (3,048 rows, FK -> host)
Phase 2: audit_message           (2,614 rows, FK -> audit_event)
Phase 3: audit_pam_event         (2,055 rows, FK -> audit_event)
         audit_service_event     (555 rows, FK -> audit_event)
         audit_user_login_event  (3 rows, FK -> audit_event)
         audit_user_cmd_event    (1 row, FK -> audit_event)
         audit_login_event       (410 rows, FK -> audit_event)
         audit_syscall_event     (8 rows, FK -> audit_event)
         audit_avc_event         (8 rows, FK -> audit_event)
         audit_proctitle_event   (8 rows, FK -> audit_event)
         (all 8 subtypes independent, can load in parallel)
```

audit_message can load in parallel with subtypes (both depend only on audit_event), but loading message first simplifies verification.

### Verification Queries: Audit Domain

```sql
-- Row counts (exact expected values for ETL verification)
SELECT 'audit_event' AS tbl, COUNT(*) AS actual, 3048 AS expected FROM audit_event
UNION ALL SELECT 'audit_message', COUNT(*), 2614 FROM audit_message
UNION ALL SELECT 'audit_pam_event', COUNT(*), 2055 FROM audit_pam_event
UNION ALL SELECT 'audit_service_event', COUNT(*), 555 FROM audit_service_event
UNION ALL SELECT 'audit_user_login_event', COUNT(*), 3 FROM audit_user_login_event
UNION ALL SELECT 'audit_user_cmd_event', COUNT(*), 1 FROM audit_user_cmd_event
UNION ALL SELECT 'audit_login_event', COUNT(*), 410 FROM audit_login_event
UNION ALL SELECT 'audit_syscall_event', COUNT(*), 8 FROM audit_syscall_event
UNION ALL SELECT 'audit_avc_event', COUNT(*), 8 FROM audit_avc_event
UNION ALL SELECT 'audit_proctitle_event', COUNT(*), 8 FROM audit_proctitle_event;

-- Subtype totality: every audit_event has exactly one subtype row
SELECT ae.event_id
FROM audit_event ae
WHERE NOT EXISTS (SELECT 1 FROM audit_pam_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_service_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_user_login_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_user_cmd_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_login_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_syscall_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_avc_event WHERE event_id = ae.event_id)
  AND NOT EXISTS (SELECT 1 FROM audit_proctitle_event WHERE event_id = ae.event_id);
-- Expected: 0 rows (every event in exactly one subtype)

-- Business key uniqueness
SELECT host_id, line_number, COUNT(*)
FROM audit_event
GROUP BY host_id, line_number
HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- Every audit_event.host_id exists in host
SELECT ae.event_id
FROM audit_event ae
LEFT JOIN host h ON ae.host_id = h.host_id
WHERE h.host_id IS NULL;
-- Expected: 0 rows

-- Per-host breakdown
SELECT h.host_key, COUNT(*) AS event_count
FROM audit_event ae
JOIN host h ON ae.host_id = h.host_id
GROUP BY h.host_key;
-- Expected: intranet_server = 2,316; internal_share = 732

-- Exfiltration spot check (internal_share, unit=put)
SELECT ae.event_id, ae.type, am.unit
FROM audit_event ae
JOIN audit_service_event ase ON ae.event_id = ase.event_id
JOIN audit_message am ON ae.event_id = am.event_id
JOIN host h ON ae.host_id = h.host_id
WHERE h.host_key = 'internal_share' AND am.unit = 'put';
-- Expected: 2 rows (SERVICE_START + SERVICE_STOP for dnsteal exfiltration)
```

---

## 3NF Transformation: Attack Labels

Source staging table: `stg_attack_label_line_raw` (61,862 rows, 6 cols).
Target: 5 normalized tables in the labels domain.
Findings doc: `docs/data_exploration/notebook_findings/naman_labels_findings.md`.
EER diagram: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.
Reference: DATA201 Lecture 4 (normalization definitions).

Implementation note: As with the other domains, 1NF and 2NF are documented as logical normalization stages. The implementation creates only the final 3NF physical tables and writes ETL that transforms directly from staging to 3NF.

### Row Grain Recap

| Staging table | Row grain | Rows | PK | Natural key(s) |
|---|---|---|---|---|
| `stg_attack_label_line_raw` | One row per labeled line in a source log file | 61,862 | `row_id` (SERIAL) | `(source_host, source_log, line_number)` verified unique, UNIQUE constraint enforced |

### Normalization Issues (Labels vs. Lecture 4)

| NF | Issue in staging | Lecture 4 view | Resolution |
|---|---|---|---|
| 1NF | `labels_json` is a JSON array of 2 to 4 label strings per record. `rules_json` is a nested JSON dict mapping labels to rule arrays. Both are multi-valued / non-atomic. | Not 1NF: cells do not hold single values. Repeating groups within a cell. | Decompose into junction tables: `labeled_line_label` (one row per label per line) and `labeled_line_rule` (one row per rule per label per line). Drop JSON columns from the line entity. |
| 2NF | After 1NF, `labeled_line` has single-column PK (`labeled_line_id`). Junction tables are all-key (composite PK with no non-key attributes). | No partial dependencies possible: single-column PKs and all-key junctions. | No schema changes. 2NF is a verification checkpoint. |
| 3NF | External functional dependency: `label_name -> attack_phase` (22 labels map to 7 phases from the project taxonomy). If phase were stored directly on the junction, it would be a transitive dependency (labeled_line_id -> label_name -> attack_phase). | Transitive dependency: non-key (label_name) determines another non-key (attack_phase). | Extract `attack_phase` lookup table (7 rows) and `attack_label` lookup table (22 rows with phase_id FK). Junctions reference `label_id` instead of label_name. |

Summary: Real schema changes occur at 1NF (explode JSON into junctions) and 3NF (phase/label lookups). 2NF adds no tables or columns.

### Logical Stage 1: 1NF Resolution

Explode 2 JSON columns from `stg_attack_label_line_raw` into junction tables. Drop `labels_json` and `rules_json` from the line entity.

New tables after 1NF:

- `labeled_line` (61,862 rows): provenance columns only (source_host, source_log, line_number).
- `labeled_line_label` (~184,517 rows): one row per (line, label). From `labels_json`: each staging row has 2 to 4 labels.
- `labeled_line_rule` (~184,651 rows): one row per (line, label, rule). From `rules_json`: each label key maps to a list of rule names.

The rule count (184,651) exceeds the label count (184,517) by 134 because some (line, label) pairs have multiple rules.

### Logical Stage 2: 2NF Verification

After 1NF, composite keys exist only in junction tables:

| Table | PK | PK type | Non-key attributes |
|---|---|---|---|
| labeled_line | `labeled_line_id` | Single-column | 3 (source_host, source_log, line_number) |
| labeled_line_label | `(labeled_line_id, label_id)` | Composite | 0 (all-key) |
| labeled_line_rule | `(labeled_line_id, label_id, rule_name)` | Composite | 0 (all-key) |

2NF result: no partial dependencies. Entity table has single-column PK. Junction tables are all-key (no non-key attributes to be partially dependent). No schema changes.

### Logical Stage 3: 3NF Resolution via Lookup Tables

The external functional dependency `label_name -> attack_phase` creates a transitive dependency if phase were stored alongside label assignments. 22 labels map to 7 attack phases (from the project taxonomy documented in `naman_labels_findings.md`).

Resolution: Extract two lookup tables:

- `attack_phase` (7 rows): one row per phase.
- `attack_label` (22 rows): one row per label with `phase_id` FK to `attack_phase`.

Junction tables reference `label_id` instead of label_name, removing the transitive dependency.

### Final 3NF Tables: Labels Domain

5 tables total.

#### attack_phase (7 rows)

3NF lookup table. Holds the 7 attack phases once; resolves the transitive dependency when phase is attached to a label. Row grain: one row per attack phase.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| phase_id | SERIAL | PK | Surrogate key |
| phase_name | VARCHAR(50) | UNIQUE, NOT NULL | Natural key |

```sql
CREATE TABLE attack_phase (
    phase_id   SERIAL PRIMARY KEY,
    phase_name VARCHAR(50) NOT NULL UNIQUE
);
```

Seed values (from project taxonomy): exfiltration, web_enumeration, initial_access, reconnaissance, privilege_escalation, password_cracking, exploitation.

ETL: Seed from project taxonomy. Not derived from staging data.

#### attack_label (22 rows)

3NF lookup table. Resolves `label_name -> attack_phase` by holding 22 label names with their phase assignment. Row grain: one row per label.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| label_id | SERIAL | PK | Surrogate key |
| label_name | VARCHAR(80) | UNIQUE, NOT NULL | Natural key |
| phase_id | INT | FK -> attack_phase, NOT NULL | Phase assignment |

```sql
CREATE TABLE attack_label (
    label_id   SERIAL PRIMARY KEY,
    label_name VARCHAR(80) NOT NULL UNIQUE,
    phase_id   INT NOT NULL REFERENCES attack_phase(phase_id)
);
```

Label-to-phase mapping (22 labels across 7 phases):

| Phase | Labels |
|---|---|
| exfiltration | attacker, dnsteal, dnsteal-received, dnsteal-dropped, exfiltration-service |
| web_enumeration | attacker_http, dirb, wpscan |
| initial_access | foothold, attacker_vpn |
| reconnaissance | service_scan, dns_scan, network_scan, traceroute |
| privilege_escalation | escalate, escalated_command, escalated_sudo_command, attacker_change_user, escalated_sudo_session |
| password_cracking | crack_passwords |
| exploitation | webshell_cmd, webshell_upload |

ETL: Seed from project taxonomy using phase_id lookup from attack_phase. Not derived from staging data.

Unknown-label policy: Every label string in `labels_json` must exist in the seeded `attack_label` table. If a label is not in the taxonomy, the ETL should fail (FK violation or explicit check).

#### labeled_line (61,862 rows)

Annotation grain entity. One row per (source_host, source_log, line_number). Provenance for joins to host and audit domains. Row grain: one row per labeled line.

| Column | Type | Constraint | Notes |
|---|---|---|---|
| labeled_line_id | SERIAL | PK | Surrogate key |
| source_host | VARCHAR(30) | NOT NULL | Same values as host.host_key |
| source_log | VARCHAR(50) | NOT NULL | Log filename the labels annotate |
| line_number | INT | NOT NULL | Line number in the raw log |

UNIQUE constraint on `(source_host, source_log, line_number)`.

```sql
CREATE TABLE labeled_line (
    labeled_line_id SERIAL PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,
    source_log      VARCHAR(50) NOT NULL,
    line_number     INTEGER NOT NULL,
    UNIQUE (source_host, source_log, line_number)
);
```

ETL: For each row in `stg_attack_label_line_raw`, insert one row with source_host, source_log, line_number. Build map `(source_host, source_log, line_number) -> labeled_line_id` for junction loading.

No FKs from `labeled_line` to other domains. Joins to host and audit use provenance columns (see Cross-Domain Relationships below).

#### labeled_line_label (~184,517 rows)

Junction table. 1NF resolution of `labels_json`. Links labeled lines to attack labels (M:N). Row grain: one row per label per line.

| Column | Type | Constraint |
|---|---|---|
| labeled_line_id | INT | PK, FK -> labeled_line(labeled_line_id) ON DELETE CASCADE |
| label_id | INT | PK, FK -> attack_label(label_id) |

```sql
CREATE TABLE labeled_line_label (
    labeled_line_id INT NOT NULL REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    label_id        INT NOT NULL REFERENCES attack_label(label_id),
    PRIMARY KEY (labeled_line_id, label_id)
);
```

ETL: For each staging row, parse `labels_json`, resolve labeled_line_id and label_id from lookup maps, insert one row per label.

#### labeled_line_rule (~184,651 rows)

Junction table. 1NF resolution of `rules_json`. Links (labeled line, label) pairs to detection rule names. Row grain: one row per rule per label per line.

Composite FK `(labeled_line_id, label_id)` to `labeled_line_label` enforces that a rule can only exist for a (line, label) pair already in the label assignment junction.

| Column | Type | Constraint |
|---|---|---|
| labeled_line_id | INT | PK, FK -> labeled_line(labeled_line_id) ON DELETE CASCADE |
| label_id | INT | PK (composite FK with labeled_line_id to labeled_line_label) |
| rule_name | VARCHAR(120) | PK, NOT NULL |

```sql
CREATE TABLE labeled_line_rule (
    labeled_line_id INT NOT NULL,
    label_id        INT NOT NULL,
    rule_name       VARCHAR(120) NOT NULL,
    PRIMARY KEY (labeled_line_id, label_id, rule_name),
    FOREIGN KEY (labeled_line_id) REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    FOREIGN KEY (labeled_line_id, label_id) REFERENCES labeled_line_label(labeled_line_id, label_id)
);
```

ETL: For each staging row, parse `rules_json` (dict of label -> list of rule names), resolve labeled_line_id and label_id, insert one row per rule per label. Must run after labeled_line_label (composite FK dependency).

### Resolved Design Decisions: Labels Domain

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| 1 | Rule as lookup table? | Keep `rule_name` as VARCHAR in `labeled_line_rule` only; no separate `rule` table | 36 distinct rule names with no additional attributes. Avoids an extra table and join. Can add a `rule` table later if rule metadata is needed. |
| 2 | labeled_line PK | Surrogate `labeled_line_id` + UNIQUE(source_host, source_log, line_number) | Simpler FKs in junctions than a 3-column composite key. |
| 3 | host_id / audit_event_id on labeled_line? | Omitted | Join via provenance columns. Adding FKs would create cross-domain coupling and complicate loading order. |
| 4 | Taxonomy source | Seeded from project taxonomy (naman_labels_findings.md, section 4) | Phases and labels are not derived from staging data. |
| 5 | Unknown labels | Fail-fast: all label strings must exist in `attack_label` | FK violation or explicit check. No auto-creation of unknown labels. |
| 6 | `labeled_line_label` as separate table | Yes, separate from `labeled_line_rule` | Simplifies queries that need only label assignments (common case). Provides composite-FK parent for `labeled_line_rule`. |

### EER Divergences: Labels Domain

| Item | This document / implementation | Current EER | Deferred resolution |
|---|---|---|---|
| Detection Rule entity | Deferred; `rule_name` stored as VARCHAR in `labeled_line_rule` | Modeled as separate entity with M:N relationship | Add rule table later if needed |
| `labeled_line_label` junction | Additional table not in EER | EER has single "Label Assignment" entity | Update EER to show two-table split |
| `attack_phase` as separate table | Extracted to resolve 3NF transitive dependency | Modeled as attribute of "Attack Label" | Expected conceptual-to-physical difference |

### 3NF Loading Order: Labels Domain

```
Phase 1: attack_phase            (7 rows, no FK deps)
Phase 2: attack_label            (22 rows, FK -> attack_phase)
Phase 3: labeled_line            (61,862 rows, no FK deps to other label tables)
Phase 4: labeled_line_label      (~184,517 rows, FK -> labeled_line, attack_label)
Phase 5: labeled_line_rule       (~184,651 rows, composite FK -> labeled_line_label; FK -> labeled_line)
```

Phase 5 must follow Phase 4 because `labeled_line_rule` has a composite FK to `labeled_line_label`.

### Verification Queries: Labels Domain

```sql
-- Row counts
SELECT 'attack_phase' AS tbl, COUNT(*) AS actual, 7 AS expected FROM attack_phase
UNION ALL SELECT 'attack_label', COUNT(*), 22 FROM attack_label
UNION ALL SELECT 'labeled_line', COUNT(*), 61862 FROM labeled_line
UNION ALL SELECT 'labeled_line_label', COUNT(*), 184517 FROM labeled_line_label
UNION ALL SELECT 'labeled_line_rule', COUNT(*), 184651 FROM labeled_line_rule;

-- Phase lookup correctness
SELECT * FROM attack_phase ORDER BY phase_id;
-- Expected: 7 rows

-- Every label has a valid phase
SELECT al.label_id, al.label_name
FROM attack_label al
LEFT JOIN attack_phase ap ON al.phase_id = ap.phase_id
WHERE ap.phase_id IS NULL;
-- Expected: 0 rows

-- Candidate key uniqueness on labeled_line
SELECT source_host, source_log, line_number, COUNT(*)
FROM labeled_line
GROUP BY source_host, source_log, line_number
HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- Per source file breakdown
SELECT source_host, source_log, COUNT(*)
FROM labeled_line
GROUP BY source_host, source_log
ORDER BY COUNT(*) DESC;
-- Expected: inet-firewall/dnsmasq.log = 54,035 (largest), etc.

-- Junction integrity: every label_id in junctions exists in attack_label
SELECT DISTINCT lll.label_id
FROM labeled_line_label lll
LEFT JOIN attack_label al ON lll.label_id = al.label_id
WHERE al.label_id IS NULL;
-- Expected: 0 rows
```

---

## Cross-Domain Relationships

### Host to Audit (FK-based)

`audit_event.host_id` references `host.host_id`. This is a direct FK relationship. When loading audit events, each source file is mapped to its host via `host.host_key = stg_audit_line_raw.source_host`.

Only 2 of 22 hosts have audit logs in scope: intranet_server (2,316 events) and internal_share (732 events).

### Host to Labels (provenance join, no FK)

`labeled_line.source_host` holds the same values as `host.host_key`. There is no FK from `labeled_line` to `host`; the link is by equality on those attributes.

```sql
SELECT ll.*, h.hostname, h.host_id
FROM labeled_line ll
JOIN host h ON h.host_key = ll.source_host;
```

All 8 label files map to 5 distinct source_host values; each exists in the 22-host inventory.

### Audit to Labels (provenance join, no FK)

Labeled lines that annotate audit logs share the same provenance as audit events: same host (via source_host = host.host_key) and same log line (source_log = 'audit.log', line_number). For audit.log only, a labeled line corresponds to at most one audit event.

```sql
SELECT ae.event_id, ae.host_id, ae.line_number,
       ll.labeled_line_id, al.label_name, ap.phase_name
FROM audit_event ae
JOIN host h ON h.host_id = ae.host_id
JOIN labeled_line ll ON ll.source_host = h.host_key
  AND ll.source_log = 'audit.log'
  AND ll.line_number = ae.line_number
JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
JOIN attack_label al ON al.label_id = lll.label_id
JOIN attack_phase ap ON ap.phase_id = al.phase_id;
```

Only 11 audit-labeled lines exist in scope: 9 from intranet_server (lines 1860 to 1868, privilege escalation) and 2 from internal_share (lines 667 to 668, data exfiltration).

---

## Full 3NF Loading Order

```
Host domain:
  Phase 1: os_release                (2 rows, no FK deps)
  Phase 2: host                      (22 rows, FK -> os_release)
  Phase 3: host_group                (63 rows, FK -> host)
           host_fqdn                 (20 rows, FK -> host)
           host_ipv4                 (24 rows, FK -> host)
           host_ipv6                 (24 rows, FK -> host)
           host_log_config           (66 rows, FK -> host)
           (all 5 independent, can load in parallel)

Labels domain (lookups first, then lines, then junctions):
  Phase 4: attack_phase              (7 rows, no FK deps)
  Phase 5: attack_label              (22 rows, FK -> attack_phase)
  Phase 6: labeled_line              (61,862 rows, no FK deps to label tables)
  Phase 7: labeled_line_label        (~184,517 rows, FK -> labeled_line, attack_label)
  Phase 8: labeled_line_rule         (~184,651 rows, composite FK -> labeled_line_label)

Audit domain (depends on host):
  Phase 4: audit_event               (3,048 rows, FK -> host)
  Phase 5: audit_message             (2,614 rows, FK -> audit_event)
  Phase 6: audit_pam_event           (2,055 rows, FK -> audit_event)
           audit_service_event       (555 rows, FK -> audit_event)
           audit_user_login_event    (3 rows, FK -> audit_event)
           audit_user_cmd_event      (1 row, FK -> audit_event)
           audit_login_event         (410 rows, FK -> audit_event)
           audit_syscall_event       (8 rows, FK -> audit_event)
           audit_avc_event           (8 rows, FK -> audit_event)
           audit_proctitle_event     (8 rows, FK -> audit_event)
           (all 8 subtypes independent, can load in parallel)
```

Labels and audit domains can load in parallel after the host domain completes. Phase numbers above represent logical ordering; labels phases 4 to 8 and audit phases 4 to 6 are independent of each other.

Total: 22 tables across 3 domains (7 host + 10 audit + 5 labels).

---

## Mid-Presentation Summary

This project normalizes security log data from the AIT Log Data Set V2.0 (russellmitchell testbed) into a 3NF relational schema in PostgreSQL. The normalization covers three domains for the mid-presentation scope:

**Host inventory** (from servers.yaml, 22 machines): 7 tables. Multi-valued fields (groups, FQDNs, IP addresses) decomposed into junction/child tables (1NF). Transitive dependency on OS release information resolved via lookup table (3NF). Central `host` table serves as the integration point for all other domains via `host_key`.

**Audit logs** (from 2 audit.log files, 3,048 events across intranet_server and internal_share): 10 tables. The `msg` TEXT blob unpacked into atomic columns in `audit_message` (1NF). 15 event types decomposed into 8 subtype tables via total, disjoint specialization (3NF), eliminating the transitive-like dependency where event type determines which columns are populated.

**Attack labels** (from 8 JSONL label files, 61,862 labeled lines across 5 hosts): 5 tables. Multi-valued JSON arrays (labels, rules) decomposed into junction tables (1NF). External taxonomy dependency (label_name -> attack_phase) resolved via lookup tables (3NF).

Cross-domain connections: audit events link to hosts via FK (`audit_event.host_id -> host.host_id`). Labels link to hosts and audit events via provenance joins on `(source_host, source_log, line_number)`, with no direct FK, preserving domain independence while enabling analytical queries across all three domains.