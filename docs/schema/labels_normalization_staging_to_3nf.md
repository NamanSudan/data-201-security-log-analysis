# Labels Normalization: Staging → 1NF → 2NF → 3NF

Design, review, and transformation logic for normalizing the **labels** staging family (`stg_attack_label_line_raw`) to 3NF. Staging is assumed already loaded and stable. This document consolidates the normalization design and the staging/3NF plan review.

**Source:** `stg_attack_label_line_raw` (61,862 rows from 8 JSONL files).  
**Findings:** `docs/data_exploration/notebook_findings/naman_labels_findings.md`.  
**ER:** `docs/er_diagrams/internal diagrams/attack_labels_er_v1_raw.drawio.xml`; 3NF: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.  
**Related:** Attack Labels section in `normalization_raw_to_3nf.md`.

**Implementation reference:** Parsers and loaders for the host domain follow a pattern in `src/parsers/final/hosts.py`, `src/models/final/host.py`, and `src/loaders/load_3nf.py`. Labels ETL should mirror that pattern: parser functions take a session and optional lookup maps and return `list[dict]` whose keys match the 3NF model columns; the loader runs phases in FK order, builds maps after each flush (e.g. `phase_name → phase_id`, `label_name → label_id`, `(source_host, source_log, line_number) → labeled_line_id` from inserted objects), and passes maps into subsequent parser functions.

---

## 1. Review summary

The design is **sound**: staging grain, 1NF→2NF→3NF path, and final table set are consistent with `naman_labels_findings.md`. The 3NF DDL in `sql/3nf/` matches this doc. **Raw files, parser, and model align with the plan; no data loss and no invented data** when normalization is applied as specified. The plan **complies with NormalizationRules** (1NF: explode arrays; 2NF: no partial dependencies; 3NF: transitive dependency resolved via lookup tables). Staging candidate key is enforced: `UNIQUE (source_host, source_log, line_number)` is in `normalization_raw_to_3nf.md` DDL and in `src/models/staging/labels.py` (`UniqueConstraint`).

---

## 2. Row grain of `stg_attack_label_line_raw`

- **Grain:** One row per **labeled line** in a source log file (one annotation record per line in one of the 8 label JSONL files).
- **Candidate key:** `(source_host, source_log, line_number)` — unique; `row_id` is surrogate PK.
- **Count:** 61,862 rows.

---

## 3. How fields change across normalization

| Field | Staging | 1NF | 2NF | 3NF |
|-------|---------|-----|-----|-----|
| **labels_json** | One TEXT cell: JSON array of 2–4 label strings. | **Removed** from line table; replaced by junction table: one row per (line, label). | No change. | Junction references **label_id** (FK to `attack_label`); label names live in `attack_label` with `phase_id`. |
| **rules_json** | One TEXT cell: JSON dict label → list of rule names. | **Removed**; replaced by junction: one row per (line, label, rule). | No change. | Junction uses **label_id** and stores `rule_name` (or optional `rule_id`). |
| **row_id** | Surrogate PK. | Not carried; 3NF line table gets its own PK (`labeled_line_id`). | — | — |
| **source_host, source_log, line_number** | Provenance / candidate key. | Stay on the single “line” entity (`labeled_line`). | No change. | Unchanged; enable join to host and audit. |

---

## 4. Staged normalization path

- **Staging → 1NF:** Remove multi-valued attributes; replace with junction tables (one row per label per line, one row per rule per label per line).
- **1NF → 2NF:** No new tables or keys; verify no partial dependencies (none found).
- **2NF → 3NF:** Resolve transitive dependency **label_name → attack_phase** (external taxonomy) via `attack_phase` and `attack_label` lookups.

**Summary:** Real schema changes occur at **1NF** (explode JSON into junctions) and **3NF** (phase/label lookups). **2NF** adds no tables or columns.

---

## 5. Per-stage design

### 5.1 Staging (current)

| Table | Row grain | PK | FKs | Major columns |
|-------|-----------|----|-----|----------------|
| `stg_attack_label_line_raw` | One per labeled line (61,862) | `row_id` | None | `source_host`, `source_log`, `line_number`, `labels_json`, `rules_json` |

Candidate key `(source_host, source_log, line_number)` is enforced via UNIQUE in DDL and in the SQLAlchemy model.

### 5.2 After 1NF

| Table | Row grain | PK | FKs | Major columns | What changed |
|-------|-----------|----|-----|----------------|---------------|
| **labeled_line** | One per labeled line (61,862) | `labeled_line_id` | None | `source_host`, `source_log`, `line_number` | Provenance only; dropped JSON columns. |
| **labeled_line_label** | One per (line, label) (~184,517) | (labeled_line_id, label_id) | → labeled_line, → attack_label | `labeled_line_id`, `label_id` | From `labels_json`: one row per label. |
| **labeled_line_rule** | One per (line, label, rule) | (labeled_line_id, label_id, rule_name) | → labeled_line_label (composite), → labeled_line (cascade) | `labeled_line_id`, `label_id`, `rule_name` | From `rules_json`: one row per rule per label. |

(At 1NF we can use `label_name` in the junctions; at 3NF we use `label_id` after introducing `attack_label`.)

### 5.3 After 2NF

No schema changes. Single-column PK on `labeled_line`; junction tables are all-key. No partial dependencies.

### 5.4 After 3NF

| Table | Row grain | PK | FKs | Major columns | What changed |
|-------|-----------|----|-----|----------------|---------------|
| **attack_phase** | One per phase (7) | `phase_id` | None | `phase_name` | New; holds 7 phases (removes transitive dependency). |
| **attack_label** | One per label (22) | `label_id` | → attack_phase | `label_name`, `phase_id` | New; FD label_name → attack_phase. |
| **labeled_line** | One per labeled line (61,862) | `labeled_line_id` | None | `source_host`, `source_log`, `line_number` | Unchanged from 1NF. |
| **labeled_line_label** | One per (line, label) (~184,517) | (labeled_line_id, label_id) | → labeled_line, → attack_label | `labeled_line_id`, `label_id` | References `label_id` instead of label name. |
| **labeled_line_rule** | One per (line, label, rule) (~184,651) | (labeled_line_id, label_id, rule_name) | → labeled_line_label (composite), → labeled_line (cascade) | `labeled_line_id`, `label_id`, `rule_name` | References `label_id`; composite FK enforces rule must belong to existing (line, label) assignment. |

---

## 6. 2NF and real schema changes

**2NF does not introduce any new tables or columns** for this family. The only structural work is at 1NF (junctions) and 3NF (phase/label lookups).

---

## 7. Recommended final 3NF table set

| Table | Purpose |
|-------|---------|
| **attack_phase** | Lookup: 7 phases (exfiltration, web_enumeration, etc.). |
| **attack_label** | Lookup: 22 labels + phase_id (satisfies label_name → attack_phase). |
| **labeled_line** | One row per (source_host, source_log, line_number); provenance for joins to host and audit. |
| **labeled_line_label** | Junction: which labels apply to which line. |
| **labeled_line_rule** | Junction: which rule fired for which label on which line. |

No separate metadata table for log-config `add_field` in the labels domain; that belongs to the host domain (`host_log_config.add_field_json`).

### Expected row counts (for loader verify_counts)

| Table | Expected count | Notes |
|-------|----------------|-------|
| attack_phase | 7 | Fixed from taxonomy. |
| attack_label | 22 | Fixed from taxonomy. |
| labeled_line | 61,862 | One per staging row. |
| labeled_line_label | 184,517 | Sum of label-array lengths across all staging rows (findings: 184,517 occurrences). |
| labeled_line_rule | 184,651 | Sum of all rule-name entries in `rules_json` across all staging rows (validated from DB). Exceeds `labeled_line_label` (184,517) by 134 because some (line, label) pairs have multiple rules. |

---

## 8. Why each final 3NF table exists

| Table | Why it exists |
|-------|----------------|
| **attack_phase** | Holds the 7 phases once; supports 3NF when phase is attached to label. |
| **attack_label** | Single place for 22 label names and their phase (FD: label_name → attack_phase). |
| **labeled_line** | Annotation grain: one row per (source_host, source_log, line_number) for joins to audit/host. |
| **labeled_line_label** | Replaces multi-valued `labels_json` with atomic (line, label) rows. |
| **labeled_line_rule** | Replaces nested `rules_json` with atomic (line, label, rule) rows; composite FK to `labeled_line_label` enforces that rules belong to existing label assignments. |

---

## 9. Relationships: labels 3NF to each other and to host/audit

### 9.1 Within the labels 3NF tables

- **attack_phase** ← **attack_label:** Each `attack_label` row has `phase_id` FK to `attack_phase`. One phase has many labels; each label has exactly one phase.
- **labeled_line** ← **labeled_line_label:** Each junction row has `labeled_line_id` FK to `labeled_line`. One labeled line has 2–4 label rows (and vice versa: many-to-many).
- **labeled_line_label** ← **labeled_line_rule:** Each rule row has a composite FK `(labeled_line_id, label_id)` to `labeled_line_label`, ensuring a rule can only exist for an existing label assignment. Also has `labeled_line_id` FK (cascade) to `labeled_line`. One label assignment has one or more rule rows.
- **attack_label** ← **labeled_line_label**, **labeled_line_rule:** Junctions reference `label_id`; each label can appear on many lines.

No FKs from `labeled_line` to other domains; joins to host and audit use provenance columns.

### 9.2 Labels 3NF to host tables

- **Relationship:** `labeled_line.source_host` holds the same values as `host.host_key` (YAML dict key / directory name: e.g. `intranet_server`, `inet-firewall`). There is **no FK** from `labeled_line` to `host`; the link is by equality on those attributes.
- **Join:** To attach host metadata (e.g. hostname, OS, groups) to a labeled line:
  ```sql
  SELECT ll.*, h.hostname, h.host_id
  FROM labeled_line ll
  JOIN host h ON h.host_key = ll.source_host
  ```
- **Scope:** All 8 label files map to 5 distinct `source_host` values; each of those should exist in `host` (same 22-host inventory as in host 3NF). Use this join when analyzing “which host this label applies to” or when building cross-domain views.

### 9.3 Labels 3NF to audit tables

- **Relationship:** Labeled lines that annotate **audit** logs share the same provenance as audit events: same host (via `source_host` = `host.host_key`) and same log line (`source_log` = `'audit.log'`, `line_number`). The audit 3NF table `audit_event` has `host_id` (FK to `host`) and `line_number` (line in that host’s audit log). So for **audit.log only**, a labeled line corresponds to at most one audit event.
- **Join:** To get labels for audit events (only for the two hosts that have audit logs in scope: intranet_server, internal_share):
  ```sql
  SELECT ae.event_id, ae.host_id, ae.line_number, ll.labeled_line_id, llb.label_id, al.label_name, ap.phase_name
  FROM audit_event ae
  JOIN host h ON h.host_id = ae.host_id
  JOIN labeled_line ll ON ll.source_host = h.host_key
    AND ll.source_log = 'audit.log'
    AND ll.line_number = ae.line_number
  JOIN labeled_line_label llb ON llb.labeled_line_id = ll.labeled_line_id
  JOIN attack_label al ON al.label_id = llb.label_id
  JOIN attack_phase ap ON ap.phase_id = al.phase_id
  ```
- **Scope:** Only rows in `labeled_line` with `source_log = 'audit.log'` (e.g. intranet_server and internal_share) have a matching `audit_event`; the other 6 label files (dnsmasq, access, error, auth, cpu, openvpn) do not have an audit_event table in the current schema, so the join above returns only the 11 audit-labeled lines (9 + 2) when used as written.

### 9.4 Summary diagram (logical)

```
host (host_id, host_key, ...)
  ^
  | host.host_key = labeled_line.source_host  [no FK]
  |
labeled_line (labeled_line_id, source_host, source_log, line_number)
  |
  +-- labeled_line_label (labeled_line_id, label_id) --> attack_label --> attack_phase
  |         ^
  |         | composite FK (labeled_line_id, label_id)
  |         |
  +-- labeled_line_rule  (labeled_line_id, label_id, rule_name)

audit_event (event_id, host_id, line_number, ...)
  |
  | join when source_log = 'audit.log':
  |   host.host_key = labeled_line.source_host
  |   AND labeled_line.line_number = audit_event.line_number
  v
labeled_line (same as above, for audit.log only)
```

---

## 10. DDL (3NF tables)

Canonical DDL files live in `sql/3nf/`: `attack_phase.sql`, `attack_label.sql`, `labeled_line.sql`, `labeled_line_label.sql`, `labeled_line_rule.sql`. Create in dependency order below.

### attack_phase

```sql
-- attack_phase: Lookup for 7 attack phases (3NF; no FKs)
-- Seed from project taxonomy (e.g. naman_labels_findings.md).

CREATE TABLE attack_phase (
    phase_id   SERIAL PRIMARY KEY,
    phase_name VARCHAR(50) NOT NULL UNIQUE
);
```

### attack_label

```sql
-- attack_label: 22 labels with phase_id (resolves FD label_name -> attack_phase)
-- Seed from project taxonomy; label_name unique.

CREATE TABLE attack_label (
    label_id   SERIAL PRIMARY KEY,
    label_name VARCHAR(80) NOT NULL UNIQUE,
    phase_id   INT NOT NULL REFERENCES attack_phase(phase_id)
);
```

### labeled_line

```sql
-- labeled_line: One row per (source_host, source_log, line_number); 61,862 rows
-- Enables join to host/audit via provenance. Surrogate PK for simpler FKs.

CREATE TABLE labeled_line (
    labeled_line_id SERIAL PRIMARY KEY,
    source_host      VARCHAR(30) NOT NULL,
    source_log       VARCHAR(50) NOT NULL,
    line_number      INTEGER NOT NULL,
    UNIQUE (source_host, source_log, line_number)
);
```

### labeled_line_label

```sql
-- labeled_line_label: Junction line <-> label (~184,517 rows)
-- 1NF resolution of labels_json.

CREATE TABLE labeled_line_label (
    labeled_line_id INT NOT NULL REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    label_id        INT NOT NULL REFERENCES attack_label(label_id),
    PRIMARY KEY (labeled_line_id, label_id)
);
```

### labeled_line_rule

```sql
-- labeled_line_rule: Junction (line, label, rule_name); one row per rule per label per line
-- 1NF resolution of rules_json. rule_name kept as string; optional rule table later.
-- VARCHAR(120) is a safe upper bound for current rule names; adjust if longer names appear.
-- Composite FK to labeled_line_label ensures a rule can only exist for
-- a (line, label) pair that is already in the label assignment junction.

CREATE TABLE labeled_line_rule (
    labeled_line_id INT NOT NULL,
    label_id        INT NOT NULL,
    rule_name       VARCHAR(120) NOT NULL,
    PRIMARY KEY (labeled_line_id, label_id, rule_name),
    FOREIGN KEY (labeled_line_id) REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    FOREIGN KEY (labeled_line_id, label_id) REFERENCES labeled_line_label(labeled_line_id, label_id)
);
```

---

## 11. ETL steps plan (staging → 3NF)

Staging is read-only; ETL writes only to the 5 3NF tables. No physical 1NF/2NF tables; transformations are logical steps in one pass.

### Prerequisites

- Staging table `stg_attack_label_line_raw` populated (61,862 rows).
- Taxonomy available: 7 phase names, 22 label names with phase assignment (e.g. from `naman_labels_findings.md` §4 or `data_scope_and_findings.md`).

### Unknown-label policy

**Fail-fast (recommended):** Every label string appearing in `labels_json` must exist in the seeded `attack_label` table. If any label in the data is not in the taxonomy, the ETL should fail (FK violation or explicit check). Do not invent new label or phase rows from the data. If a future dataset may introduce new labels, define an "unknown" phase and an "unknown" label in the seed list and document that unmapped labels are assigned to them.

### Seed data: machine-readable taxonomy for attack_phase and attack_label

Phases and labels are **not** derived from staging; they come from the project taxonomy. Implementations need a machine-readable source so the loader can insert rows and build `phase_name → phase_id` and `label_name → label_id` maps. Recommended approach:

- **Define in code** (e.g. in `src/parsers/final/labels.py` or a dedicated data module): (1) an ordered list of 7 `phase_name` values, and (2) a mapping of each of the 22 label names to a phase name (e.g. `LABEL_TO_PHASE: dict[str, str]` or a list of `(label_name, phase_name)` pairs). The canonical mapping is in `naman_labels_findings.md` §4 (table "Label Taxonomy (22 Labels, 7 Attack Phases)").
- **Loader:** Insert phases in order → flush → build `phase_name → phase_id`. Insert labels using that map to set `phase_id` → flush → build `label_name → label_id`. Use these maps in the junction parsers.

Example structure (snake_case phase names):  
`PHASE_NAMES = ["exfiltration", "web_enumeration", "initial_access", "reconnaissance", "privilege_escalation", "password_cracking", "exploitation"]`  
`LABEL_TO_PHASE = {"attacker": "exfiltration", "dnsteal": "exfiltration", "dnsteal-received": "exfiltration", "dnsteal-dropped": "exfiltration", "exfiltration-service": "exfiltration", "attacker_http": "web_enumeration", "dirb": "web_enumeration", "wpscan": "web_enumeration", "foothold": "initial_access", "attacker_vpn": "initial_access", "service_scan": "reconnaissance", "dns_scan": "reconnaissance", "network_scan": "reconnaissance", "traceroute": "reconnaissance", "escalate": "privilege_escalation", "escalated_command": "privilege_escalation", "escalated_sudo_command": "privilege_escalation", "attacker_change_user": "privilege_escalation", "escalated_sudo_session": "privilege_escalation", "crack_passwords": "password_cracking", "webshell_cmd": "exploitation", "webshell_upload": "exploitation"}`

### Seed data: exact phase_name values

Use one consistent convention for `phase_name` so seed data and ETL agree. Recommended (snake_case):

- `exfiltration`, `web_enumeration`, `initial_access`, `reconnaissance`, `privilege_escalation`, `password_cracking`, `exploitation`

Alternatively, use the title-case names from `naman_labels_findings.md` §4 (Exfiltration, Web Enumeration, …) if that is the project standard. List the exact 7 values in the ETL or seed script.

### Load order (respect FKs)

1. **attack_phase** (no FKs)
2. **attack_label** (FK → attack_phase)
3. **labeled_line** (no FKs to other 3NF label tables)
4. **labeled_line_label** (FK → labeled_line, attack_label)
5. **labeled_line_rule** (composite FK → labeled_line_label; FK → labeled_line)

Step 5 must run after Step 4 because `labeled_line_rule` has a composite FK to `labeled_line_label`.

---

### Step 1: Seed attack_phase

- Insert 7 rows into `attack_phase` using the exact `phase_name` list chosen above.
- Build in-memory map: `phase_name → phase_id` for Step 2.

---

### Step 2: Seed attack_label

- For each of the 22 labels (from taxonomy), look up `phase_id` from the phase map.
- Insert one row per label into `attack_label` (`label_name`, `phase_id`).
- Build in-memory map: `label_name → label_id` for Steps 4 and 5.

---

### Step 3: Load labeled_line

- For each row in `stg_attack_label_line_raw`, insert one row into `labeled_line`:
  - `source_host`, `source_log`, `line_number` from staging.
  - Rely on SERIAL for `labeled_line_id`.
- After insert (or using RETURNING), build map: `(source_host, source_log, line_number) → labeled_line_id` for Steps 4 and 5.
- Verification: `SELECT COUNT(*) FROM labeled_line` = 61,862.

---

### Step 4: Load labeled_line_label

- For each row in `stg_attack_label_line_raw`:
  - Parse `labels_json` (e.g. `json.loads(labels_json)`).
  - Resolve `labeled_line_id` from the map from Step 3.
  - For each label string in the array:
    - Resolve `label_id` from the label_name → label_id map (fail if missing, per unknown-label policy).
    - Insert one row into `labeled_line_label` (`labeled_line_id`, `label_id`).
- For idempotent runs, use `INSERT ... ON CONFLICT (labeled_line_id, label_id) DO NOTHING` if acceptable; otherwise duplicate keys cause insert failure.
- Verification: row count ~184,517; no duplicate (labeled_line_id, label_id).

---

### Step 5: Load labeled_line_rule

- For each row in `stg_attack_label_line_raw`:
  - Parse `rules_json` (e.g. `json.loads(rules_json)`); structure: `{ "label_name": ["rule1", "rule2"], ... }`.
  - Resolve `labeled_line_id` from the map from Step 3.
  - For each label key and each rule name in its list:
    - Resolve `label_id` from the label_name → label_id map.
    - Insert one row into `labeled_line_rule` (`labeled_line_id`, `label_id`, `rule_name`).
- For idempotent runs, use `INSERT ... ON CONFLICT (labeled_line_id, label_id, rule_name) DO NOTHING` if acceptable.
- Verification: row count consistent with sum of rule list lengths across all staging rows; no duplicate (labeled_line_id, label_id, rule_name).

---

### Step 6: Integrity checks (optional)

- Every `labeled_line_id` in `labeled_line_label` and `labeled_line_rule` exists in `labeled_line`.
- Every `label_id` exists in `attack_label` and every `attack_label.phase_id` exists in `attack_phase`.
- For each staging row, number of `labeled_line_label` rows for that line = length of `labels_json` array.
- For each staging row, number of `labeled_line_rule` rows = total number of rule names in `rules_json` (sum over all label keys).

**Loader verify_integrity:** The loader can implement a `verify_integrity` step for the labels domain (mirroring the host loader). FKs enforce that every `label_id` and `labeled_line_id` in the junctions exists in the parent tables; optional checks include comparing junction row counts to the expected counts above or to sums computed from staging JSON.

---

## 12. Design decisions (recommended)

| Decision | Recommendation |
|----------|----------------|
| Rule as lookup table | Keep `rule_name` in `labeled_line_rule` only; add `rule` table later if needed. |
| labeled_line PK | Surrogate `labeled_line_id` + UNIQUE(source_host, source_log, line_number). |
| host_id / audit_event_id on labeled_line | Omit initially; join via (source_host, source_log, line_number) to host and audit. |
| Taxonomy source | Seed `attack_phase` and `attack_label` from project taxonomy (e.g. naman_labels_findings.md §4). |
| Unknown labels | Fail-fast: all label strings must exist in `attack_label`; or document an "unknown" phase/label. |
| Rule-to-label integrity | `labeled_line_rule` has composite FK `(labeled_line_id, label_id)` to `labeled_line_label`, enforcing that a rule can only exist for an existing label assignment. Step 5 must follow Step 4 in ETL. |

### EER divergences (physical schema vs. `combined_eer_3nf_v1.drawio.xml`)

This document is the **implementation source of truth** for the labels domain. The EER diagram (`combined_eer_3nf_v1.drawio.xml`) is the conceptual-level reference. Three intentional divergences exist between the physical schema defined here and the current EER:

1. **Detection Rule entity deferred.** The EER models "Detection Rule" as a separate entity with `rule_name` as its key attribute, connected M:N to "Label Assignment" via a "triggered by" relationship. The physical schema keeps `rule_name` as a `VARCHAR(120)` string directly in `labeled_line_rule` with no `detection_rule` lookup table. This avoids an extra table and join for a 36-value set with no additional attributes. A `rule` table can be added later if rule metadata or strict referential integrity on rule names is needed.

2. **`labeled_line_label` is an additional junction not in the EER.** The EER models a single "Label Assignment" associative entity at grain (annotation, label, rule). The physical schema splits this into two tables: `labeled_line_label` at grain (line, label) and `labeled_line_rule` at grain (line, label, rule). The additional `labeled_line_label` table simplifies queries that need only label assignments without rules (the common case for analytical queries) and provides a composite-FK parent for `labeled_line_rule`.

3. **`attack_phase` extracted to separate table.** The EER models `attack_phase` as a regular attribute of "Attack Label." The physical schema creates a separate `attack_phase` table to resolve the 3NF transitive dependency `label_name -> attack_phase`. This is the expected conceptual-to-physical difference.

EER reconciliation (updating the diagram to match the physical schema) is deferred to a separate task.

---

## 13. Verification: plan vs. raw files and staging code

### Raw label files (`russellmitchell/labels/`)

There are **8 JSONL files**; the parser’s `LABEL_FILE_CONFIG` maps each to `source_host` and `source_log`. **JSON schema (per line):** Exactly three fields: `line` (int), `labels` (array of str), `rules` (object: label → list of rule names). Sampled raw content matches the plan; `rules` keys match `labels` entries. Staging grain and column mapping are correct.

### Staging parser and model

Parser produces `source_host`, `source_log`, `line_number` (from `obj["line"]`), `labels_json`, `rules_json`; blank lines skipped. Model defines `stg_attack_label_line_raw` with `UniqueConstraint("source_host", "source_log", "line_number")`. No data loss; expected staging count 61,862.

### Data-loss and invented-data

- **No data loss:** Raw → staging: all three JSON fields stored. Staging → 3NF: one `labeled_line` per staging row; one `labeled_line_label` per label in `labels_json`; one `labeled_line_rule` per (label, rule) in `rules_json`. Lookup tables are seeded from taxonomy; every raw label string must exist in taxonomy (or documented "unknown" policy).
- **No invented data:** Fact rows only from raw or taxonomy. `attack_phase` and `attack_label` rows come from project taxonomy only.

---

## 14. NormalizationRules compliance

- **1NF:** Staging multi-valued `labels_json` and `rules_json` resolved by junction tables so each cell holds one value. ✓
- **2NF:** `labeled_line` has single-column PK; junction tables are all-key; no partial dependencies. ✓
- **3NF:** Transitive dependency `label_name → attack_phase` resolved by `attack_phase` and `attack_label`; junctions reference `label_id`. ✓
- **Process:** Staging → 1NF (explode) → 2NF (verify) → 3NF (lookups). ✓

---

## 15. Unresolved / deferred and checklist

- **rule table:** Optional; add if rule metadata or strict referential integrity on rule names is required. See EER divergences in §12.
- **Explicit host_id / audit_event_id on labeled_line:** Deferred; join via provenance (see §9).
- **Exact phase/label seed content:** Taken from project taxonomy (naman_labels_findings §4); list exact 7 `phase_name` values in ETL or seed script.
- **EER reconciliation:** Update `combined_eer_3nf_v1.drawio.xml` to reflect the physical schema divergences documented in §12.

**Checklist for implementation:**

- [x] Add `UNIQUE (source_host, source_log, line_number)` to staging DDL and SQLAlchemy model.
- [ ] Update `naman_labels_findings.md` staging DDL to use `VARCHAR(30)` / `VARCHAR(50)` for provenance columns (align with audit).
- [x] Document unknown-label policy (fail-fast or "unknown" label) in this doc (§11).
- [x] Document exact 7 `phase_name` seed values / convention (§11).
- [ ] (Optional) Document or implement `ON CONFLICT DO NOTHING` for junction inserts (§11 Steps 4–5).
- [x] Note on `rule_name` max length: VARCHAR(120) as safe upper bound (§10 DDL).
- [x] Add composite FK from `labeled_line_rule(labeled_line_id, label_id)` to `labeled_line_label` (§10 DDL, §12).
- [x] Document EER divergences: Detection Rule deferred, `labeled_line_label` added, `attack_phase` extracted (§12).
- [x] Add exact `labeled_line_rule` expected count: 184,651 (§7).

---

## 16. Concise live walkthrough

1. **Staging grain:** One row = one labeled line: (source_host, source_log, line_number) plus labels and rules as JSON.
2. **1NF:** Replace multi-valued columns with junctions: one table for (line, label) and one for (line, label, rule). Provenance stays on `labeled_line`.
3. **2NF:** Check partial dependencies; none (single-column line PK, all-key junctions). No schema change.
4. **3NF:** Resolve label_name → attack_phase by adding `attack_phase` and `attack_label`; junctions reference `label_id`.
5. **Final set:** `attack_phase`, `attack_label`, `labeled_line`, `labeled_line_label`, `labeled_line_rule`. ETL: seed phases and labels from taxonomy, load lines from staging, then explode JSON into the two junction tables.
6. **Cross-domain:** Join `labeled_line` to `host` on `host.host_key = labeled_line.source_host`. Join to `audit_event` when `source_log = 'audit.log'` via `host` and `line_number` to get labels for audit events.
