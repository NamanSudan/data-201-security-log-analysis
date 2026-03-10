# Audit Log Findings - intranet_server

Source: `russellmitchell/gather/intranet_server/logs/audit/audit.log` (2,316 lines, Linux auditd format).
Labels: `russellmitchell/labels/intranet_server/logs/audit/audit.log` (9 labeled lines).
Analysis notebook: `notebooks/05_explore_audit_intranet.ipynb`.
Parsed staging table: `stg_audit_line_raw` (43 columns, 2,316 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued field:** The `msg` column contains multiple key-value pairs packed into a single text field (e.g., `op=PAM:accounting acct="root" exe="/usr/sbin/cron" hostname=? addr=? terminal=cron res=success`). This is a 1NF violation-multiple distinct values (operation, account, executable, hostname, address, terminal, result) stored in one cell. Same pattern as `groups TEXT` and `add_field_json TEXT` in `stg_host_raw`.

The `msg` field is non-null for ~86% of rows (PAM events, SERVICE events, USER_LOGIN, USER_CMD). It is NULL for LOGIN, AVC, SYSCALL, and PROCTITLE event types, which carry their fields as top-level key-value pairs.

Note: the companion label file has multi-valued fields (`labels` is an array, `rules` is a nested dict), but those belong to DAT-48, not this raw table.

**1NF status: violated.** The `msg` column packs multiple key-value pairs into a single text blob. Normalization should unpack it into separate columns (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd).

### 2NF Check

The raw table uses a single-column surrogate primary key (`row_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

Event type strongly correlates with which fields are populated. For example, LOGIN events populate `old_auid`, `old_ses`, `tty`, `res` but never `msg_unit`, `msg_comm`, `apparmor`, etc. This is `row_id -> type -> field_set`, a transitive chain where a non-key attribute determines other non-key attributes.

**3NF status: structural heterogeneity noted.** The type -> field_set correlation may motivate subtype modeling in the final design.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `row_id` | all other attributes | Surrogate PK. |
| FD2 | `(source_host, source_log, line_number)` | all other attributes | Each line in a given source file is unique. Staging candidate key across files. |
| FD3 | `type` | populated field set | Each event type uses a specific subset of columns (structural heterogeneity, normalization input). |
| FD4 | `serial` | `epoch`, `timestamp` | All rows with the same serial share the same timestamp (multi-line events). |
| FD5 | `old_auid` | constant `4294967295` | All 304 LOGIN events have old_auid = 4294967295. Trivial (only one value). |

---

## 2. Field-by-Field Summary

### Core fields (present in all/most event types)

| Field | Present | Unique | Notes |
|---|---|---|---|
| `line_number` | 2316/2316 | 2316 | 1-based, candidate key |
| `type` | 2316/2316 | 15 | Event type (see distribution below) |
| `epoch` | 2316/2316 | 1272 | Unix timestamp with ms precision |
| `serial` | 2316/2316 | 2308 | 8 duplicates across 4 multi-line events |
| `timestamp` | 2316/2316 | 1272 | Derived from epoch (TSTZ) |
| `pid` | 2312/2316 | 312 | Max 31519, fits INTEGER |
| `uid` | 2308/2316 | 3 | 0 (root), 33 (www-data), 1002 (jhall) |
| `auid` | 2308/2316 | 3 | 0, 1002, 4294967295 (unset sentinel; requires BIGINT) |
| `ses` | 2308/2316 | 306 | 4294967295 in 1092 rows (47.2%); requires BIGINT |

### msg field (raw nested blob, 1NF violation)

| Field | Present | Notes |
|---|---|---|
| `msg` | 2000 (86.4%) | Full `msg='...'` string stored as-is. Contains multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd). NULL for LOGIN, AVC, SYSCALL, PROCTITLE event types. |

When unpacked during normalization, the msg blob contains these sub-fields: op (6 distinct values), acct (2: root, jhall), exe (5: /usr/sbin/cron, /lib/systemd/systemd, /usr/sbin/sshd, /bin/su, /usr/bin/sudo), hostname (2: ?, 172.19.131.174), addr (2), terminal (6), res (always "success"), unit (17 distinct), comm (always "systemd"), id (always 1002), cwd (1 value), cmd (1 hex value).

### Type-specific fields (high sparsity)

| Field | Present | Event types | Notes |
|---|---|---|---|
| `old_auid`, `old_ses` | 304 (13.1%) | LOGIN | Always 4294967295 |
| `tty` | 308 (13.3%) | LOGIN, USER_LOGIN | "(none)" for LOGIN, "ssh" for USER_LOGIN |
| `res` | 304 (13.1%) | LOGIN | Always "1" (success) |
| `apparmor`, `operation`, `info`, `profile`, `name` | 4 (0.2%) | AVC | AppArmor policy events |
| `arch`, `syscall`, `success`, `exit`, `a0`-`a3`, `items`, `ppid`, `gid`, `euid`, `suid`, `fsuid`, `egid`, `sgid`, `fsgid`, `exe`, `key` | 4 (0.2%) | SYSCALL | Kernel syscall audit |
| `proctitle` | 4 (0.2%) | PROCTITLE | Hex-encoded command line |
| `comm` | 8 (0.3%) | AVC, SYSCALL | "apparmor_parser" (AVC), "apparmor_parser" (SYSCALL) |

---

## 3. Event Type Distribution

| Event type | Count | % | Category |
|---|---|---|---|
| CRED_ACQ | 308 | 13.3% | PAM |
| USER_START | 306 | 13.2% | PAM |
| USER_ACCT | 305 | 13.2% | PAM |
| LOGIN | 304 | 13.1% | Login |
| CRED_DISP | 302 | 13.0% | PAM |
| USER_END | 302 | 13.0% | PAM |
| SERVICE_START | 241 | 10.4% | Service |
| SERVICE_STOP | 230 | 9.9% | Service |
| AVC | 4 | 0.2% | Kernel |
| SYSCALL | 4 | 0.2% | Kernel |
| PROCTITLE | 4 | 0.2% | Kernel |
| USER_LOGIN | 3 | 0.1% | Login |
| USER_AUTH | 1 | 0.04% | PAM |
| USER_CMD | 1 | 0.04% | Command |
| CRED_REFR | 1 | 0.04% | PAM |

Dominant pattern: ~64% cron PAM cycles (root, /usr/sbin/cron), ~20% systemd service start/stop. Labeled lines: 9 (0.4%).

---

## 4. Labeled Lines (Ground Truth Labels)

9 labeled lines (1860-1868), all privilege escalation:

- **Lines 1860-1863** (4 lines): `su` from www-data (uid 33) to jhall via `/bin/su`. Labels: `attacker_change_user`, `escalate`. The attacker (IP 172.19.131.174) had SSH access as jhall, then used `su` to escalate.
- **Lines 1864-1868** (5 lines): `sudo cat /etc/shadow` by jhall via `/usr/bin/sudo`. Labels: `escalated_command`, `escalated_sudo_command`, `escalate`. Reading the shadow password file is a classic post-exploitation move.

Label distribution: `escalate` (9), `escalated_command` (5), `escalated_sudo_command` (5), `attacker_change_user` (4).

The attacker IP 172.19.131.174 appears in 21 rows total, including 3 USER_LOGIN (SSH) events for uid 1002 (jhall).

---

## 5. Multi-Line Events (Serial Grouping)

4 serials (529-532) span 3 lines each: AVC + SYSCALL + PROCTITLE. These are kernel-level AppArmor events grouped by serial number. The remaining 2,304 serials each have exactly 1 line.

Serial grouping is an important design input; final grain will be decided in schema finalization docs. The staging table keeps them as separate rows.

---

## 6. Parsed Staging DDL

43 columns. This file maps to the shared staging table shape `stg_audit_line_raw`; `source_host` and `source_log` distinguish records from different audit sources. The `msg` field stores the full `msg='...'` string as a single TEXT blob (1NF violation-normalization unpacks it). Type inference assumptions are documented in `type_inference_assumptions.md` (data-201/ root).

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

1. **1NF violation (msg column):** The `msg` TEXT column packs multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) into a single text blob. Normalization should unpack these into separate columns. Same pattern as `groups TEXT` in `stg_host_raw`.

2. **Structural heterogeneity (type -> field_set):** The 15 event types each use a different subset of columns. This may motivate subtype modeling in the final design (e.g., `audit_pam_events`, `audit_login_events`, `audit_service_events`, `audit_syscall_events`) with shared columns in a parent table and type-specific columns in subtypes.

3. **Unset sentinel values:** auid=4294967295 and ses=4294967295 appear in 1,092 rows (47.2%), representing system processes without interactive login sessions. Normalization should decide: store as-is, convert to NULL, or add a flag column.

4. **Dual result fields:** PAM events have `msg_res` ("success"/"failed" text) packed inside the msg blob, LOGIN uses `res` ("1"/"0" numeric string) as a top-level field. Normalization should unify into a single result representation.

5. **Hex-encoded fields:** The msg blob in USER_CMD contains hex-encoded command data. `proctitle` (PROCTITLE events) contains hex-encoded command line. Normalization should decide whether to store decoded values alongside raw hex.

6. **Cross-file synthesis with internal_share audit.log (DAT-36):** This file and `internal_share` share the same auditd source format and may share a common final audit schema after cross-file synthesis. The intranet_server file (2,316 rows) covers privilege escalation; the internal_share file covers exfiltration.

7. **Serial-grouped events:** 4 multi-line events (AVC+SYSCALL+PROCTITLE) share a serial. Serial grouping is an important design input; final grain will be decided in schema finalization docs.
