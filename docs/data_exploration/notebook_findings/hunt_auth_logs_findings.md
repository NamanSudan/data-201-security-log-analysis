# Auth Log Findings - intranet_server/auth.log

Source: `russellmitchell/gather/intranet_server/logs/auth.log` (272 lines, Linux auth/syslog format).
Labels: `russellmitchell/labels/intranet_server/logs/auth.log` (8 labeled lines).
Analysis notebook: `notebooks/08_explore_auth_logs.ipynb`.
Target table: `auth_events` (this file contributes 272 events; labels map into `attack_labels` during normalization).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued fields (labels file):**
Each labeled record contains:
- `labels`: an **array** of tags (e.g., `["escalate", "escalated_command", ...]`)
- `rules`: a **nested dict** mapping label → list of matched signatures

These are 1NF violations (collections stored in a single field). In the planned normalized design, these unpack into separate rows in `attack_labels` linked to the parent event in `log_events`.

**Embedded key-value “sub-fields” (raw auth.log):**
Some `message` values (notably `sudo`) embed multiple attributes in a single text blob:
`TTY=... ; PWD=... ; USER=... ; COMMAND=...`

This is also a 1NF violation if stored as one column. Resolution direction: parse into separate columns (terminal, working_dir, target_user, command) during normalization/ETL while retaining the raw message.

**1NF status: violated.**

### 2NF Check

Raw loading uses a single-column surrogate primary key (e.g., `auth_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

**Transitive dependency (type determines schema):**
`process_name` / event family determines which sub-fields exist and which parsing rules apply:
- CRON PAM session open/close lines contain `user` and sometimes `(uid=...)`
- sshd “Accepted ...” lines contain username + remote IP/port + auth method
- sudo command lines contain TTY/PWD/USER/COMMAND
- systemd-logind lines contain session ids and usernames

This is analogous to the intranet audit log finding (`type -> populated field set`).

**3NF status: violated.** Resolution direction: a parent `log_events` + subtype table (`auth_events`) plus type-specific parsing/columns and/or subtype tables if needed.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `auth_event_id` | all other attributes | Surrogate PK. |
| FD2 | `line_number` | all other attributes | Each log line is unique. Candidate key. |
| FD3 | `process_name` | populated field set | Process family determines which fields can be parsed (3NF issue). |
| FD4 | `hostname` | constant `intranet-server` | Single host within this file; meaningful only after unioning multiple hosts. |

---

## 2. Field-by-Field Summary (auth.log)

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---:|---:|---|
| `line_number` | 272/272 | 272 | 1-based line number; candidate key |
| `event_timestamp` | 272/272 | ~many | Syslog timestamp without year (month/day/time) |
| `hostname` | 272/272 | 1 | Always `intranet-server` |
| `process_name` | 272/272 | 6 | `CRON`, `sshd`, `sudo`, `su`, `systemd-logind`, `systemd` |
| `message` | 272/272 | ~many | Free text; must be `TEXT` |

### Common parsed fields (high coverage, analysis-only)

Following the `05_explore_audit_intranet.ipynb` pattern, the notebook should keep two views:
- `df`: includes parsed sub-fields for **field-by-field exploration**
- `df_raw`: keeps only the **raw blob** columns (DDL must match `df_raw`, not `df`)

The fields below are useful for analysis, but are **parsed from `message`** and therefore belong in `df` (and the normalized schema), not the raw table DDL.

| Field | Present | Notes |
|---|---:|---|
| `pid` | 267/272 | Present for most processes; missing on `sudo` and some `systemd` lines |
| `username` | 264/272 | Parsable from CRON/sshd/sudo/su/session lines; multi-principal su line complicates mapping |
| `uid` | 129/272 | Present in “by (uid=...)” patterns; observed values: 0, 33 |

### Low-frequency but high-signal parsed fields (analysis-only)

| Field | Present | Notes |
|---|---:|---|
| `remote_ip`, `remote_port` | 1/272 | From `sshd` “Accepted ... from <ip> port <port>”; observed IP `172.19.131.174` |
| `auth_method` | 1/272 | From `sshd` accept line; observed `publickey` |
| `terminal` | 3/272 | From `sudo` (TTY=...) and su `+ /dev/pts/...` line (requires trimming whitespace) |
| `pwd` | 2/272 | From `sudo` command lines |
| `target_user` | 3/272 | From `su` (target) and `sudo` (USER=...) |
| `command` | 2/272 | From `sudo` command lines |
| `session_id` | 3/272 | From systemd-logind “New/Removed session ...” |

Data quality note: some parsed substrings have trailing whitespace (e.g., `TTY=pts/1 `, `USER=root `) and should be `.strip()`’d in ETL.

---

## 3. Event Type Distribution

Dominant pattern: CRON PAM session churn.

| Event type (derived) | Count | % |
|---|---:|---:|
| `cron_session_open` | 128 | 47.1% |
| `cron_session_close` | 129 | 47.4% |
| *(all non-CRON combined)* | 15 | 5.5% |

Non-CRON breakdown (15 lines total):
- sshd: accept/open/close + one probe (`Did not receive identification string`)
- su: successful su + session open + one “+ tty user:target” audit-style line
- sudo: 2 command lines + session open/close
- systemd-logind/systemd: session lifecycle lines

---

## 4. Attack Events (Ground Truth Labels)

8 labeled lines (145–152), all privilege escalation / post-exploitation behavior:

- **Lines 145–148** (4 lines): user change + session creation
  - `su` indicates **successful** switch to `jhall` by `www-data`
  - followed by `pam_unix(su:session)` open and `systemd-logind` “New session ... of user jhall”
  - Labels: `attacker_change_user`, `escalate`

- **Lines 149–152** (4 lines): elevated commands via sudo
  - `sudo` command execution as root, including `COMMAND=/bin/cat /etc/shadow`
  - session open/close recorded by PAM
  - Labels: `escalate`, `escalated_command`, `escalated_sudo_command`, `escalated_sudo_session`

Label distribution (8 labeled records):
- `escalate` (8)
- `attacker_change_user` (4)
- `escalated_command` (5)
- `escalated_sudo_command` (5)
- `escalated_sudo_session` (3)

Signature highlights:
- `attacker.escalate.su.login` (su escalation)
- `attacker.escalate.sudo.command` (sudo command execution)
- `attacker.escalate.sudo.open` (sudo session open)
- `attacker.escalate.systemd.newsession.after` (session creation after escalation)
- `attacker.escalate.audit.sudo.command.start` (cross-log correlation with auditd)

---

## 5. Key Findings for Schema Design

1. **CRON dominates (94.5% of lines):** analysts must filter CRON to see interactive activity. Keep CRON records for completeness, but expect most security queries to exclude them.

2. **Auth “event types” are implicit:** `process_name` + message pattern is required to derive an `event_type` useful for analytics (e.g., `ssh_accepted`, `sudo_command`, `cron_session_open`).

3. **High-signal sudo lines are structured:** parsing `TTY`, `PWD`, `USER`, and `COMMAND` provides strong investigative value (who did what as whom, from where).

4. **User attribution can require multiple principals:** `su` lines include *actor* (`www-data`) and *target* (`jhall`). A single `username` column loses information; consider `actor_username` and `target_username` in normalization.

5. **Labels/rules must normalize:** arrays/dicts in the label file should map to `attack_labels` (one row per label per event) and optionally `attack_label_rules` (one row per rule signature per label per event).

---

## 6. DDL for Raw Loading (auth.log + labels)

This raw-load shape follows the project rule **Raw = truly raw**:
- Keep `message` as a single TEXT blob (1NF violation when it embeds multiple attributes)
- Do **not** store message-parsed sub-fields (username, uid, tty, command, remote_ip, etc.) in the raw DDL
- Multi-valued `labels` and nested `rules` from the label file are stored as-is (1NF violations; normalization unpacks them)

```sql
-- PostgreSQL
CREATE TABLE auth_events_raw (
    auth_event_id          SERIAL PRIMARY KEY,
    line_number            INTEGER NOT NULL,
    event_timestamp        TIMESTAMP,
    hostname               VARCHAR(100),
    process_name           VARCHAR(50) NOT NULL,
    pid                    INTEGER,
    message                TEXT NOT NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE auth_events_raw (
    auth_event_id          INT AUTO_INCREMENT PRIMARY KEY,
    line_number            INT NOT NULL,
    event_timestamp        DATETIME,
    hostname               VARCHAR(100),
    process_name           VARCHAR(50) NOT NULL,
    pid                    INT,
    message                TEXT NOT NULL,
    created_at             DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Notes for Normalization Phase

1. **Unpack labels/rules to `attack_labels`:** Each (event, label) becomes one row; each (event, label, signature) becomes one row if signatures are modeled separately.

2. **Derive `event_type`:** normalize common event families (cron session open/close, ssh accept/close, su, sudo) for consistent analytics.

3. **Parse sudo sub-fields:** extract `terminal`, `pwd`, `target_user`, `command` into columns (and standardize whitespace).

4. **Handle multi-principal events:** model `actor_username` and `target_username` (especially for `su` / `sudo`) so escalation chains can be reconstructed.

5. **Join with audit.log for complete auth_events:** planned `auth_events` table is sourced from both `auth.log` and auditd (`audit.log`). Some attributes (e.g., `exe`, `op`, `acct`, unified `result`) are richer/easier to extract from auditd and should be reconciled during integration.