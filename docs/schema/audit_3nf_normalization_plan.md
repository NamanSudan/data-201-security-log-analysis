# Audit Log 3NF Normalization Plan

**Status:** Design only. No implementation until approved.

**Constraint:** Implementation must use **new files only**. Do not edit or change any existing code, migrations, or documentation. This plan is self-contained; existing `data_model_3nf.md` and `normalization_raw_to_3nf.md` remain unchanged.

---

## 1. Scope

- **In scope:** `stg_audit_line_raw` → 3NF audit entities only (intranet_server + internal_share, 3,048 rows).
- **Out of scope:** Labels 3NF, hosts (already done), other log types. Host/labels are referenced only for FKs and join keys.

**References (read-only):**

- Staging: `src/models/staging/audit.py`, `src/parsers/staging/audit.py`, `src/loaders/load_staging.py`
- Notebooks: 01_explore_hosts, 05_explore_audit_intranet, 07_explore_audit_internal_share, 09_explore_labels
- Findings: `docs/data_exploration/notebook_findings/naman_audit_intranet_findings.md`, `naman_audit_internal_share_findings.md`
- Target EER: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`
- **DATA201 Lecture 4 – Normalization** (Dr. Guannan Liu, SJSU): definitions of 1NF, 2NF, 3NF, functional dependencies, partial/transitive dependencies, and anomalies used below.
- **Normalization rules sheet:** `docs/er_diagrams/normalization_rules_sheet (1).md` (Lecture 4/5 checklist; use to verify raw data and design).

---

## 2. Current State (Audit)

| Layer        | What exists |
|-------------|-------------|
| Staging model | `StgAuditLineRaw`: 43 columns, `row_id` PK, `msg` TEXT blob (1NF violation), type-specific columns. |
| Parser      | `parse_audit_files()` → list of dicts; `msg` stored as-is. |
| Loader      | Staging loader inserts into `stg_audit_line_raw`; no 3NF audit load. |
| 3NF loader  | Host domain only; no audit. |

---

## 3. Normalization Framework (DATA201 Lecture 4)

Definitions below follow **DATA201 Lecture 4 – Normalization** (Database Technologies for Data Intelligence Applications, SJSU). The audit design is checked against these rules.

### 3.1 Normal forms

- **1NF (First Normal Form):** Every column holds a **single value** (atomic). No lists, no repeating groups. One row = one fact; table is truly tabular (rows × columns). Violation example: a cell containing `[P10, P20, P30]` instead of one value per row.
- **2NF (Second Normal Form):** Table is in 1NF and has **no partial dependencies**. Every non-key attribute must depend on the **whole** key, not on only part of it. (Relevant when the key is composite, e.g. (OrderID, ProductID).)
- **3NF (Third Normal Form):** Table is in 2NF and has **no transitive dependencies**. Every non-key attribute must depend **only on the key**, not on another non-key (no chain Key → B → C where B and C are non-key).

### 3.2 Functional dependency (FD)

- **FD:** \(X \rightarrow Y\) means: if two rows have the same value of \(X\), they must have the same value of \(Y\). \(X\) = determinant; \(Y\) = dependent. FDs are determined by **business rules**, not only by current data.
- **Key / candidate key:** A set of attributes that uniquely identifies each row; **minimal** (no extra columns). A **composite key** is two or more columns that together form the key.
- **Partial dependency:** A non-key attribute depends on only **part** of a composite key (violates 2NF).
- **Transitive dependency:** Key → non-key A → non-key B; i.e. a non-key depends on another non-key (violates 3NF).

### 3.3 Anomalies normalization addresses

- **Update anomaly:** Changing a fact (e.g. customer email) requires updating many rows → risk of inconsistency.
- **Insert anomaly:** Cannot add an entity (e.g. new product) without creating a fake related row (e.g. fake order).
- **Delete anomaly:** Deleting a row loses the only copy of some fact (e.g. deleting last order loses customer).

---

## 4. Normalization Issues Addressed (Audit vs. Lecture 4)

Application of the above framework to `stg_audit_line_raw`:

| NF  | Issue in staging | Lecture 4 view | Resolution in this plan |
|-----|-------------------|----------------|--------------------------|
| **1NF** | `msg` holds multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) in one cell — a repeating group / non-atomic value. | Not 1NF: one cell does not hold a single value. | Unpack into atomic attributes in a separate **audit_message** table (0..1 per audit event). Each attribute is one column, one value per row. |
| **2NF** | Staging uses surrogate `row_id`; natural candidate key is `(source_host, source_log, line_number)` or `(host_id, line_number)`. Attributes like `type`, `epoch`, `pid` depend on the whole key. | With composite key, we require no partial dependency: no non-key attribute may depend on only part of the key. | 3NF schema uses `(host_id, line_number)` as business key; **audit_event** has no partial dependency (all non-keys depend on event_id / whole key). Subtypes use `event_id` as sole key; no composite key, so 2NF holds. |
| **3NF** | Event **type** determines which other columns are populated (e.g. LOGIN → old_auid, old_ses, tty, res; SYSCALL → syscall, arch, success, …). So in one wide table, non-key attributes effectively depend on another non-key (type), i.e. transitive-like structure. | Transitive dependency: Key → type → field set. Non-key depending on non-key. | Split by **subtype tables**: each subtype table’s non-key attributes depend only on **event_id** (the key). Type is stored once in **audit_event**; type-specific attributes live in the subtype that corresponds to that type, so there is no “non-key → non-key” dependency in a single table. |

Anomalies avoided by this design: **update** (change msg content in one row of audit_message); **insert** (add event without forcing duplicate msg columns across subtypes); **delete** (delete an event does not leave orphaned msg attributes in a mixed table).

---

## 5. Target Design (EER-Aligned)

- **No `log_line` table** for audit-only scope; `audit_event` holds `host_id`, `line_number`, `raw_line`.
- **Shared `audit_message`** table (0..1 per event) for the 12 unpacked msg attributes; msg-bearing subtypes do not duplicate these columns.
- **8 subtype tables** (total, disjoint): Pam, Service, User Login, User Command (msg-bearing); Login, Syscall, Avc, Proctitle (outer-field).

---

## 6. Table Definitions

### 6.1 audit_event (supertype)

| Column      | Type              | Constraint | Notes |
|------------|-------------------|------------|--------|
| event_id   | SERIAL / INT      | PK         | Surrogate. |
| host_id    | INT               | NOT NULL, FK → host(host_id) | From `host.host_key = source_host`. |
| line_number| INT               | NOT NULL   | Per-file line number. |
| raw_line   | TEXT              | NOT NULL   | Full line (provenance). |
| type       | VARCHAR(20)       | NOT NULL   | Discriminator (15 values across both files). |
| epoch      | DOUBLE PRECISION  | NOT NULL  | |
| serial     | INT               | NOT NULL  | |
| timestamp  | TIMESTAMPTZ       | NOT NULL  | |
| pid        | INT               | nullable  | |
| uid        | INT               | nullable  | |
| auid       | BIGINT            | nullable  | 4294967295 = unset sentinel. |
| ses        | BIGINT            | nullable  | 4294967295 = unset sentinel. |

- **Unique:** `(host_id, line_number)`.
- **Row count:** 3,048.
- **3NF:** Key = event_id (surrogate). Every non-key attribute (host_id, line_number, raw_line, type, epoch, serial, timestamp, pid, uid, auid, ses) depends only on event_id. host_id is FK to host (separate entity); no transitive dependency within this table.

### 6.2 audit_message (1NF resolution; 0..1 per audit_event)

| Column   | Type         | Constraint | Notes |
|----------|--------------|------------|--------|
| event_id | INT          | PK, FK → audit_event(event_id) | 1:1 from event side, 0..1 from message side. |
| op       | VARCHAR(30)  | nullable   | |
| acct     | VARCHAR(50)  | nullable   | |
| exe      | TEXT         | nullable   | |
| hostname | VARCHAR(50)  | nullable   | PAM/msg hostname (not host entity). |
| addr     | VARCHAR(50)  | nullable   | |
| terminal | VARCHAR(30)  | nullable   | |
| res      | VARCHAR(20)  | nullable   | e.g. "success". |
| unit     | VARCHAR(100) | nullable   | Service unit (SERVICE_*). |
| comm     | VARCHAR(50)  | nullable   | |
| id       | INT          | nullable   | USER_CMD. |
| cwd      | TEXT         | nullable   | USER_CMD. |
| cmd      | TEXT         | nullable   | USER_CMD (hex). |

- **Row count:** ~2,540 (events with non-null `msg` in staging).
- **3NF:** Key = event_id (FK to audit_event). Every non-key (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) depends only on event_id. 1NF fix: each attribute is atomic (one value per cell); no repeating group.

### 6.3 Subtype tables (8; total, disjoint)

Each subtype has **event_id** as PK and FK → `audit_event(event_id)`. Exactly one subtype row per audit_event. **3NF:** Each table’s only key is `event_id`; every non-key attribute (if any) depends only on `event_id` (no partial dependency, no transitive dependency).

---

#### 6.3.1 audit_pam_event (msg-bearing)

| Column    | Type        | Constraint | Notes |
|-----------|-------------|------------|--------|
| event_id  | INT         | PK, FK → audit_event(event_id) | Same key as supertype. |

- **Event types:** CRED_ACQ, USER_ACCT, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR.
- **Row count:** ~1,968 (approx.). Validate from staging.
- **3NF:** Single-column key; no other attributes. Type-specific content lives in **audit_message** (0..1), so no duplication of msg attributes across subtypes.

---

#### 6.3.2 audit_service_event (msg-bearing)

| Column    | Type        | Constraint | Notes |
|-----------|-------------|------------|--------|
| event_id  | INT         | PK, FK → audit_event(event_id) | Same key as supertype. |

- **Event types:** SERVICE_START, SERVICE_STOP.
- **Row count:** 555 (471 intranet + 84 internal_share).
- **3NF:** Single-column key; no other attributes. Service fields (unit, comm, exe, etc.) in **audit_message** only.

---

#### 6.3.3 audit_user_login_event (msg-bearing)

| Column    | Type        | Constraint | Notes |
|-----------|-------------|------------|--------|
| event_id  | INT         | PK, FK → audit_event(event_id) | Same key as supertype. |

- **Event types:** USER_LOGIN.
- **Row count:** 3.
- **3NF:** Single-column key; no other attributes. Msg content in **audit_message** only.

---

#### 6.3.4 audit_user_cmd_event (msg-bearing)

| Column    | Type        | Constraint | Notes |
|-----------|-------------|------------|--------|
| event_id  | INT         | PK, FK → audit_event(event_id) | Same key as supertype. |

- **Event types:** USER_CMD.
- **Row count:** 1.
- **3NF:** Single-column key; no other attributes. cmd, cwd, id in **audit_message** only.

---

#### 6.3.5 audit_login_event (outer-field)

| Column    | Type         | Constraint | Notes |
|-----------|--------------|------------|--------|
| event_id  | INT          | PK, FK → audit_event(event_id) | Same key as supertype. |
| old_auid  | BIGINT       | nullable   | LOGIN top-level; often 4294967295. |
| old_ses   | BIGINT       | nullable   | LOGIN top-level; often 4294967295. |
| tty       | VARCHAR(30)  | nullable   | e.g. "(none)". |
| res       | VARCHAR(10)  | nullable   | e.g. "1" (success). |

- **Event types:** LOGIN.
- **Row count:** 410 (304 intranet + 106 internal_share).
- **3NF:** Key = event_id; every non-key (old_auid, old_ses, tty, res) depends only on event_id. No transitive dependency.

---

#### 6.3.6 audit_syscall_event (outer-field)

| Column    | Type         | Constraint | Notes |
|-----------|--------------|------------|--------|
| event_id  | INT          | PK, FK → audit_event(event_id) | Same key as supertype. |
| arch      | VARCHAR(20)  | nullable   | e.g. x86_64. |
| syscall   | INT          | nullable   | Syscall number. |
| success   | VARCHAR(5)   | nullable   | e.g. yes/no. |
| exit      | BIGINT       | nullable   | Exit code. |
| exe       | TEXT         | nullable   | Executable path. |
| comm      | VARCHAR(50)  | nullable   | Command name. |
| key       | VARCHAR(20)  | nullable   | Audit key. |

Optional (low-value; see §10): a0, a1, a2, a3 VARCHAR(20); items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid INT.

- **Event types:** SYSCALL.
- **Row count:** 8 (4 intranet + 4 internal_share).
- **3NF:** Key = event_id; all non-keys depend only on event_id. No partial or transitive dependency.

---

#### 6.3.7 audit_avc_event (outer-field)

| Column     | Type         | Constraint | Notes |
|------------|--------------|------------|--------|
| event_id   | INT          | PK, FK → audit_event(event_id) | Same key as supertype. |
| apparmor   | VARCHAR(20)  | nullable   | AppArmor subystem. |
| operation  | VARCHAR(30)  | nullable   | e.g. profile_replace. |
| profile    | VARCHAR(50)  | nullable   | Profile name. |
| name       | TEXT         | nullable   | Resource name. |
| info       | TEXT         | nullable   | Additional info. |
| comm       | VARCHAR(50)  | nullable   | Command. |

- **Event types:** AVC.
- **Row count:** 8 (4 intranet + 4 internal_share).
- **3NF:** Key = event_id; every non-key depends only on event_id. No transitive dependency.

---

#### 6.3.8 audit_proctitle_event (outer-field)

| Column     | Type   | Constraint | Notes |
|------------|--------|------------|--------|
| event_id   | INT    | PK, FK → audit_event(event_id) | Same key as supertype. |
| proctitle  | TEXT   | nullable   | Hex-encoded command line. |

- **Event types:** PROCTITLE.
- **Row count:** 8 (4 intranet + 4 internal_share).
- **3NF:** Key = event_id; proctitle depends only on event_id. No transitive dependency.

---

#### 6.3.9 Subtype summary

| Subtype table            | Key      | Non-key columns | 3NF |
|--------------------------|----------|------------------|-----|
| audit_pam_event          | event_id | none             | Single key; msg in audit_message. |
| audit_service_event       | event_id | none             | Single key; msg in audit_message. |
| audit_user_login_event    | event_id | none             | Single key; msg in audit_message. |
| audit_user_cmd_event      | event_id | none             | Single key; msg in audit_message. |
| audit_login_event         | event_id | old_auid, old_ses, tty, res | All depend only on event_id. |
| audit_syscall_event       | event_id | arch, syscall, success, exit, exe, comm, key (+ optional) | All depend only on event_id. |
| audit_avc_event           | event_id | apparmor, operation, profile, name, info, comm | All depend only on event_id. |
| audit_proctitle_event     | event_id | proctitle        | Single non-key; depends only on event_id. |

**Total subtype rows:** 3,048 (one per audit_event). Validate exact counts from staging during implementation.

---

## 7. Implementation: New Files Only

All of the following must be **new** files or new sections; do not modify existing files.

| Purpose        | New file(s) / location |
|----------------|-------------------------|
| 3NF ORM models | **New** `src/models/final/audit.py` only. Do not edit `src/models/final/__init__.py` or any existing model file. |
| Migrations     | **New** Alembic revision(s) under `alembic/versions/` (e.g. `xxx_add_audit_3nf_tables.py`). |
| Msg unpacking | **New** module (e.g. `src/parsers/final/audit.py`). Do not change `src/parsers/staging/audit.py`. |
| 3NF load      | **New** module (e.g. `src/loaders/load_3nf_audit.py`) that reads from `stg_audit_line_raw` and writes to the new tables. Do not edit `src/loaders/load_3nf.py` or `load_staging.py`. Invoke the audit load via a new script or entrypoint (e.g. `python -m src.loaders.load_3nf_audit`) rather than by changing existing loaders. |

**Rule:** No edits to any existing files—no schema docs, no staging models/parsers/loaders, no existing migrations, no existing `__init__.py`. This document is the single source of truth for the audit 3NF design.

---

## 8. Load Order and ETL Logic

1. **audit_event:** For each row in `stg_audit_line_raw`, resolve `host_id` via `host.host_key = source_host`; insert one row per staging row (event_id generated).
2. **audit_message:** For each staging row where `msg` is not null, parse `msg` into the 12 attributes; insert one row per such event with `event_id` from step 1.
3. **Subtypes:** For each audit_event, route by `type` and insert exactly one row into the corresponding subtype table with the same `event_id`.

Host resolution: build a map `source_host` → `host_id` from the existing `host` table; use it when building audit_event rows.

---

## 9. Validation (Post-Implementation)

- **Counts:** audit_event = 3,048; audit_message ≤ 3,048; sum of 8 subtype row counts = 3,048; each event_id in exactly one subtype.
- **Integrity:** Every audit_event.host_id exists in host; every audit_message.event_id and every subtype.event_id exists in audit_event.
- **Spot checks:** Exfiltration (internal_share, unit=put) present in audit_event + audit_service_event + audit_message; privilege escalation (intranet, lines 1860–1868) in audit_event + appropriate subtypes + audit_message.

---

## 10. Open Decisions (Resolve Before Implementation)

1. **Sentinel values:** Store auid/ses = 4294967295 as-is vs. NULL vs. add a flag column.
2. **Result fields:** Unify PAM (msg) and LOGIN (top-level) result into one representation in audit_message and audit_login_event if desired.
3. **Low-value syscall columns:** Include a0–a3, items, ppid, gid, euid, suid, fsuid, egid, sgid, fsgid in audit_syscall_event or omit (document choice in this doc or a short addendum).
4. **log_line table:** Omitted for audit-only; introduce later if other log types are normalized under a shared Log Line superclass.

---

*End of plan. Implementation must not change any existing files; use new files only.*
