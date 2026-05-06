# Audit Log Findings - internal_share

Source: `russellmitchell/gather/internal_share/logs/audit/audit.log` (732 lines, Linux auditd format).
Labels: `russellmitchell/labels/internal_share/logs/audit/audit.log` (2 labeled lines).
Analysis notebook: `notebooks/07_explore_audit_internal_share.ipynb`.
Parsed staging table: `stg_audit_line_raw` (43 columns, 732 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued field:** The `msg` column contains multiple key-value pairs packed into a single text field (e.g., `op=PAM:accounting acct="root" exe="/usr/sbin/cron" hostname=? addr=? terminal=cron res=success`). This is a 1NF violation-multiple distinct values (operation, account, executable, hostname, address, terminal, result) stored in one cell. Same pattern as `msg` in intranet_server audit log (DAT-42) and `groups TEXT` in `stg_host_raw`.

The `msg` field is non-null for ~83.9% of rows (PAM events and SERVICE events). It is NULL for LOGIN, AVC, SYSCALL, and PROCTITLE event types, which carry their fields as top-level key-value pairs.

| Field | Violation | Values per row | Distinct sub-fields | Resolution direction |
|---|---|---|---|---|
| `msg` | Multi-valued (key-value pairs packed in TEXT blob) | 5-7 sub-fields | op, acct, exe, hostname, addr, terminal, res, unit, comm | Unpack into separate columns during normalization |

**1NF status: VIOLATED.**

### 2NF Check

The raw table uses a single-column surrogate primary key (`row_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: SATISFIED.**

### 3NF Check

Event type strongly correlates with which fields are populated. For example, LOGIN events populate `old_auid`, `old_ses`, `tty`, `res` but never `msg` or `apparmor`; SERVICE events populate `msg` (with unit, comm, exe) but never `old_auid` or `arch`. This is `row_id -> type -> field_set`, a transitive chain where a non-key attribute determines other non-key attributes.

**3NF status: structural heterogeneity noted.** The type -> field_set correlation may motivate subtype modeling in the final design.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `row_id` | all other attributes | Surrogate PK. |
| FD2 | `(source_host, source_log, line_number)` | all other attributes | Each line in a given source file is unique. Staging candidate key across files. |
| FD3 | `type` | populated field set | Each event type uses a specific subset of columns (structural heterogeneity, normalization input). |
| FD4 | `serial` | `epoch`, `timestamp` | All rows with the same serial share the same timestamp (multi-line events). |
| FD5 | `old_auid` | constant `4294967295` | All 106 LOGIN events have old_auid = 4294967295. Trivial (only one value). |

---

## 2. Field-by-Field Summary

### Core fields (present in all/most event types)

| Field | Present | Unique | Notes |
|---|---|---|---|
| `line_number` | 732/732 | 732 | 1-based, candidate key |
| `type` | 732/732 | 11 | Event type (see distribution below) |
| `epoch` | 732/732 | 360 | Unix timestamp with ms precision |
| `serial` | 732/732 | 724 | 8 duplicates across 4 multi-line events |
| `timestamp` | 732/732 | 360 | Derived from epoch (TSTZ) |
| `pid` | 728/732 | 108 | Max ~15520, fits INTEGER |
| `uid` | 724/732 | 1 | 0 (root) only |
| `auid` | 724/732 | 2 | 0, 4294967295 (unset sentinel; requires BIGINT) |
| `ses` | 724/732 | 107 | 4294967295 in 300 rows (41.0%); requires BIGINT |

### msg field (raw nested blob, 1NF violation)

| Field | Present | Notes |
|---|---|---|
| `msg` | 614 (83.9%) | Full `msg='...'` string stored as-is. Contains multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res for PAM; unit, comm, exe, hostname, addr, terminal, res for SERVICE). NULL for LOGIN, AVC, SYSCALL, PROCTITLE event types. |

When unpacked during normalization, the msg blob contains these sub-fields: op (4 distinct values: PAM:accounting, PAM:setcred, PAM:session_open, PAM:session_close), acct (1: root), exe (2: /usr/sbin/cron, /lib/systemd/systemd), hostname (1: ?), addr (1: ?), terminal (2: cron, ?), res (1: success), unit (multiple: apt-daily, apport, motd-news, ssh, systemd-udevd, etc.), comm (1: systemd).

### Type-specific fields (high sparsity)

| Field | Present | Event types | Notes |
|---|---|---|---|
| `old_auid`, `old_ses` | 106 (14.5%) | LOGIN | Always 4294967295 |
| `tty` | 110 (15.0%) | LOGIN, SYSCALL | "(none)" for LOGIN, "pts0" for SYSCALL |
| `res` | 106 (14.5%) | LOGIN | Always "1" (success) |
| `apparmor`, `operation`, `profile`, `name` | 4 (0.5%) | AVC | AppArmor profile_replace events for dhclient |
| `arch`, `syscall`, `success`, `exit`, `a0`-`a3`, `items`, `ppid`, `gid`, `euid`, `suid`, `fsuid`, `egid`, `sgid`, `fsgid`, `exe`, `key` | 4 (0.5%) | SYSCALL | Kernel syscall audit (apparmor_parser) |
| `proctitle` | 4 (0.5%) | PROCTITLE | Hex-encoded: "apparmor_parser -r -T -W /etc/apparmor.d/sbin.dhclient" |
| `comm` | 8 (1.1%) | AVC, SYSCALL | "apparmor_parser" |

---

## 3. Event Type Distribution

| Event type | Count | % | Category |
|---|---|---|---|
| USER_ACCT | 106 | 14.5% | PAM |
| CRED_ACQ | 106 | 14.5% | PAM |
| LOGIN | 106 | 14.5% | Login |
| USER_START | 106 | 14.5% | PAM |
| CRED_DISP | 106 | 14.5% | PAM |
| USER_END | 106 | 14.5% | PAM |
| SERVICE_START | 47 | 6.4% | Service |
| SERVICE_STOP | 37 | 5.1% | Service |
| AVC | 4 | 0.5% | Kernel |
| SYSCALL | 4 | 0.5% | Kernel |
| PROCTITLE | 4 | 0.5% | Kernel |

Dominant pattern: ~72.4% cron PAM cycles (root, /usr/sbin/cron), ~11.5% systemd service start/stop, ~1.6% kernel (AppArmor). Labeled lines: 2 (0.3%).

Compared to intranet_server (DAT-42): 4 event types missing (USER_LOGIN, USER_AUTH, USER_CMD, CRED_REFR). Those types are SSH login and privilege escalation events that only appear on the intranet_server.

---

## 4. Labeled Lines (Ground Truth Labels)

2 labeled lines (667-668), both exfiltration service:

- **Line 667**: `SERVICE_START` for `unit=put` via `/lib/systemd/systemd`. Labels: `dnsteal`, `exfiltration-service`, `attacker`. The attacker started a service named "put" on the file server to exfiltrate data via DNS tunneling.
- **Line 668**: `SERVICE_STOP` for `unit=put` via `/lib/systemd/systemd`. Same labels. The exfiltration service stopped.

Both events share the same epoch (1643032239.298 = 2022-01-24 13:50:39 UTC) with consecutive serials (807, 808). The service started and stopped at the same millisecond, suggesting a quick burst or an artifact of the simulation.

Label distribution: `dnsteal` (2), `exfiltration-service` (2), `attacker` (2). All 3 labels co-occur on both lines.

Rule triggered: `exfil.service` (6 total label-rule associations across 2 lines).

The attacker IP (172.19.131.174) does NOT appear in this log. All hostname=? and addr=?. The exfiltration service was started via a mechanism not captured by auditd on this host (likely remote command execution after lateral movement from intranet_server).

---

## 5. Multi-Line Events (Serial Grouping)

4 serials (193-196) span 3 lines each: AVC + SYSCALL + PROCTITLE. These are kernel-level AppArmor profile_replace events for dhclient, occurring on 2022-01-21 (day 1, well before the attack). Not attack-related. The remaining 720 serials each have exactly 1 line.

Normalization decision: same as intranet_server-keep as separate rows (preserving 1:1 line mapping).

---

## 6. Parsed Staging DDL

43 columns. This file maps to the shared staging table shape `stg_audit_line_raw`, the same shape as the intranet_server audit log (DAT-42). The `source_host` and `source_log` columns distinguish records from different audit sources. The `msg` field stores the full `msg='...'` string as a single TEXT blob (1NF violation). Some columns from the intranet_server schema (e.g., `info`) are entirely NULL in this file but retained for schema compatibility.

```sql
-- PostgreSQL
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

```sql
-- MySQL
CREATE TABLE stg_audit_line_raw (
    row_id          INT AUTO_INCREMENT PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,
    source_log      VARCHAR(50) NOT NULL,
    line_number     INT NOT NULL,
    raw_line        TEXT NOT NULL,
    type            VARCHAR(20) NOT NULL,
    epoch           DOUBLE NOT NULL,
    serial          INT NOT NULL,
    timestamp       DATETIME NOT NULL,
    pid             INT,
    uid             INT,
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
    syscall         INT,
    success         VARCHAR(5),
    exit            BIGINT,
    a0              VARCHAR(20),
    a1              VARCHAR(20),
    a2              VARCHAR(20),
    a3              VARCHAR(20),
    items           INT,
    ppid            INT,
    gid             INT,
    euid            INT,
    suid            INT,
    fsuid           INT,
    egid            INT,
    sgid            INT,
    fsgid           INT,
    `key`           VARCHAR(20),
    proctitle       TEXT
);
```

---

## 7. Notes for Normalization Phase

1. **1NF violation (msg column):** Same as intranet_server. The `msg` TEXT column packs multiple key-value pairs into a single text blob. Normalization should unpack into separate columns. Same pattern as `groups TEXT` in `stg_host_raw`.

2. **Structural heterogeneity (type -> field_set):** The 11 event types each use a different subset of columns. This may motivate subtype modeling in the final design. Since the internal_share has fewer event types than intranet_server (11 vs 15), the subtypes are a subset.

3. **Unset sentinel values:** auid=4294967295 and ses=4294967295 appear in 300 rows (41.0%), representing system processes without interactive login sessions. Same handling as intranet_server: store as-is, convert to NULL, or add a flag column.

4. **Dual result fields:** Same as intranet_server. PAM events have `msg_res` ("success" text) packed inside the msg blob; LOGIN uses `res` ("1" numeric string) as a top-level field. Normalization should unify.

5. **Hex-encoded fields:** `proctitle` (PROCTITLE events) contains hex-encoded command line. No USER_CMD events in this file, so no hex-encoded cmd field. Normalization should decide whether to store decoded values alongside raw hex.

6. **Cross-file synthesis with intranet_server audit.log (DAT-42):** This file shares the auditd source format with the intranet audit log and will be reconciled in the final audit schema design. The intranet_server file (2,316 rows) covers privilege escalation; the internal_share file (732 rows) covers exfiltration. Combined: 3,048 rows.

7. **Serial-grouped events:** 4 multi-line events (AVC+SYSCALL+PROCTITLE) share a serial. Same handling as intranet_server: keep as separate rows in the raw table.

8. **No network context:** Unlike intranet_server (which has 21 rows with real IP 172.19.131.174 from SSH logins), the internal_share log has no real network addresses. All hostname=?, addr=?. The attacker's lateral movement to this host is not visible in auditd-it would be visible in other log sources (e.g., auth.log or network logs).