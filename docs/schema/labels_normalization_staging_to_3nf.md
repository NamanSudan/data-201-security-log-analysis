# Labels Normalization: Staging → 1NF → 2NF → 3NF

Design and transformation logic for normalizing the **labels** staging family (`stg_attack_label_line_raw`) to 3NF. Staging is assumed already loaded and stable.

**Source:** `stg_attack_label_line_raw` (61,862 rows from 8 JSONL files).  
**Findings:** `docs/data_exploration/notebook_findings/naman_labels_findings.md`.  
**ER:** `docs/er_diagrams/internal diagrams/attack_labels_er_v1_raw.drawio.xml`; 3NF: `docs/er_diagrams/combined_eer_3nf_v1.drawio.xml`.

---

## 1. Row grain of `stg_attack_label_line_raw`

- **Grain:** One row per **labeled line** in a source log file (one annotation record per line in one of the 8 label JSONL files).
- **Candidate key:** `(source_host, source_log, line_number)` — unique; `row_id` is surrogate PK.
- **Count:** 61,862 rows.

---

## 2. How fields change across normalization

| Field | Staging | 1NF | 2NF | 3NF |
|-------|---------|-----|-----|-----|
| **labels_json** | One TEXT cell: JSON array of 2–4 label strings. | **Removed** from line table; replaced by junction table: one row per (line, label). | No change. | Junction references **label_id** (FK to `attack_label`); label names live in `attack_label` with `phase_id`. |
| **rules_json** | One TEXT cell: JSON dict label → list of rule names. | **Removed**; replaced by junction: one row per (line, label, rule). | No change. | Junction uses **label_id** and stores `rule_name` (or optional `rule_id`). |
| **row_id** | Surrogate PK. | Not carried; 3NF line table gets its own PK (`labeled_line_id`). | — | — |
| **source_host, source_log, line_number** | Provenance / candidate key. | Stay on the single “line” entity (`labeled_line`). | No change. | Unchanged; enable join to host/audit. |

---

## 3. Staged normalization path

- **Staging → 1NF:** Remove multi-valued attributes; replace with junction tables (one row per label per line, one row per rule per label per line).
- **1NF → 2NF:** No new tables or keys; verify no partial dependencies (none found).
- **2NF → 3NF:** Resolve transitive dependency **label_name → attack_phase** (external taxonomy) via `attack_phase` and `attack_label` lookups.

**Summary:** Real schema changes occur at **1NF** (explode JSON into junctions) and **3NF** (phase/label lookups). **2NF** adds no tables or columns.

---

## 4. Per-stage design

### 4.1 Staging (current)

| Table | Row grain | PK | FKs | Major columns |
|-------|-----------|----|-----|----------------|
| `stg_attack_label_line_raw` | One per labeled line (61,862) | `row_id` | None | `source_host`, `source_log`, `line_number`, `labels_json`, `rules_json` |

### 4.2 After 1NF

| Table | Row grain | PK | FKs | Major columns | What changed |
|-------|-----------|----|-----|----------------|---------------|
| **labeled_line** | One per labeled line (61,862) | `labeled_line_id` | None | `source_host`, `source_log`, `line_number` | Provenance only; dropped JSON columns. |
| **labeled_line_label** | One per (line, label) (~184,517) | (labeled_line_id, label_id) | → labeled_line, → attack_label | `labeled_line_id`, `label_id` | From `labels_json`: one row per label. |
| **labeled_line_rule** | One per (line, label, rule) | (labeled_line_id, label_id, rule_name) | → labeled_line, → attack_label | `labeled_line_id`, `label_id`, `rule_name` | From `rules_json`: one row per rule per label. |

(At 1NF we can use `label_name` in the junctions; at 3NF we use `label_id` after introducing `attack_label`.)

### 4.3 After 2NF

No schema changes. Single-column PK on `labeled_line`; junction tables are all-key. No partial dependencies.

### 4.4 After 3NF

| Table | Row grain | PK | FKs | Major columns | What changed |
|-------|-----------|----|-----|----------------|---------------|
| **attack_phase** | One per phase (7) | `phase_id` | None | `phase_name` | New; holds 7 phases (removes transitive dependency). |
| **attack_label** | One per label (22) | `label_id` | → attack_phase | `label_name`, `phase_id` | New; FD label_name → attack_phase. |
| **labeled_line** | One per labeled line (61,862) | `labeled_line_id` | None | `source_host`, `source_log`, `line_number` | Unchanged from 1NF. |
| **labeled_line_label** | One per (line, label) (~184,517) | (labeled_line_id, label_id) | → labeled_line, → attack_label | `labeled_line_id`, `label_id` | References `label_id` instead of label name. |
| **labeled_line_rule** | One per (line, label, rule) | (labeled_line_id, label_id, rule_name) | → labeled_line, → attack_label | `labeled_line_id`, `label_id`, `rule_name` | References `label_id`. |

---

## 5. 2NF and real schema changes

**2NF does not introduce any new tables or columns** for this family. The only structural work is at 1NF (junctions) and 3NF (phase/label lookups).

---

## 6. Recommended final 3NF table set

| Table | Purpose |
|-------|---------|
| **attack_phase** | Lookup: 7 phases (exfiltration, web_enumeration, etc.). |
| **attack_label** | Lookup: 22 labels + phase_id (satisfies label_name → attack_phase). |
| **labeled_line** | One row per (source_host, source_log, line_number); provenance for joins. |
| **labeled_line_label** | Junction: which labels apply to which line. |
| **labeled_line_rule** | Junction: which rule fired for which label on which line. |

No separate metadata table for log-config `add_field` in the labels domain; that belongs to the host domain (`host_log_config.add_field_json`).

---

## 7. Why each final 3NF table exists

| Table | Why it exists |
|-------|----------------|
| **attack_phase** | Holds the 7 phases once; supports 3NF when phase is attached to label. |
| **attack_label** | Single place for 22 label names and their phase (FD: label_name → attack_phase). |
| **labeled_line** | Annotation grain: one row per (source_host, source_log, line_number) for joins to audit/host. |
| **labeled_line_label** | Replaces multi-valued `labels_json` with atomic (line, label) rows. |
| **labeled_line_rule** | Replaces nested `rules_json` with atomic (line, label, rule) rows; preserves “rules keys = labels” via FKs. |

---

## 8. DDL (3NF tables)

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

CREATE TABLE labeled_line_rule (
    labeled_line_id INT NOT NULL REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    label_id        INT NOT NULL REFERENCES attack_label(label_id),
    rule_name       VARCHAR(120) NOT NULL,
    PRIMARY KEY (labeled_line_id, label_id, rule_name)
);
```

---

## 9. ETL steps plan (staging → 3NF)

Staging is read-only; ETL writes only to the 5 3NF tables. No physical 1NF/2NF tables; transformations are logical steps in one pass.

### Prerequisites

- Staging table `stg_attack_label_line_raw` populated (61,862 rows).
- Taxonomy available: 7 phase names, 22 label names with phase assignment (e.g. from `naman_labels_findings.md` or `data_scope_and_findings.md`).

### Load order (respect FKs)

1. **attack_phase** (no FKs)  
2. **attack_label** (FK → attack_phase)  
3. **labeled_line** (no FKs to other 3NF label tables)  
4. **labeled_line_label** (FK → labeled_line, attack_label)  
5. **labeled_line_rule** (FK → labeled_line, attack_label)  

Steps 4 and 5 can run in any order after 1–3.

---

### Step 1: Seed attack_phase

- Insert 7 rows into `attack_phase` from taxonomy (e.g. Exfiltration, Web Enumeration, Initial Access, Reconnaissance, Privilege Escalation, Password Cracking, Exploitation).
- Use consistent `phase_name` values (e.g. snake_case: `exfiltration`, `web_enumeration`, …) for use in seed data and ETL.
- Build in-memory map: `phase_name → phase_id` for Step 2.

---

### Step 2: Seed attack_label

- For each of the 22 labels, look up `phase_id` from the phase map.
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
    - Resolve `label_id` from the label_name → label_id map.
    - Insert one row into `labeled_line_label` (`labeled_line_id`, `label_id`).
- Ignore duplicates if any (composite PK will reject; ensure source has no duplicate labels per line).
- Verification: row count ~184,517; no duplicate (labeled_line_id, label_id).

---

### Step 5: Load labeled_line_rule

- For each row in `stg_attack_label_line_raw`:
  - Parse `rules_json` (e.g. `json.loads(rules_json)`); structure: `{ "label_name": ["rule1", "rule2"], ... }`.
  - Resolve `labeled_line_id` from the map from Step 3.
  - For each label key and each rule name in its list:
    - Resolve `label_id` from the label_name → label_id map.
    - Insert one row into `labeled_line_rule` (`labeled_line_id`, `label_id`, `rule_name`).
- Verification: row count consistent with sum of rule list lengths across all staging rows; no duplicate (labeled_line_id, label_id, rule_name).

---

### Step 6: Integrity checks (optional)

- Every `labeled_line_id` in `labeled_line_label` and `labeled_line_rule` exists in `labeled_line`.
- Every `label_id` exists in `attack_label` and every `attack_label.phase_id` exists in `attack_phase`.
- For each staging row, number of `labeled_line_label` rows for that line = length of `labels_json` array.
- For each staging row, number of `labeled_line_rule` rows = total number of rule names in `rules_json` (sum over all label keys).

---

## 10. Design decisions (recommended)

| Decision | Recommendation |
|----------|----------------|
| Rule as lookup table | Keep `rule_name` in `labeled_line_rule` only; add `rule` table later if needed. |
| labeled_line PK | Surrogate `labeled_line_id` + UNIQUE(source_host, source_log, line_number). |
| host_id / audit_event_id on labeled_line | Omit initially; join via (source_host, source_log, line_number). |
| Taxonomy source | Seed `attack_phase` and `attack_label` from project taxonomy (e.g. naman_labels_findings.md). |

---

## 11. Unresolved / deferred

- **rule table:** Optional; add if rule metadata or strict referential integrity is required.
- **Explicit host_id / audit_event_id on labeled_line:** Deferred; join via provenance for now.
- **Exact phase/label seed content:** To be taken from project taxonomy (e.g. naman_labels_findings §4); no open design choice.

---

## 12. Concise live walkthrough

1. **Staging grain:** One row = one labeled line: (source_host, source_log, line_number) plus labels and rules as JSON.
2. **1NF:** Replace multi-valued columns with junctions: one table for (line, label) and one for (line, label, rule). Provenance stays on `labeled_line`.
3. **2NF:** Check partial dependencies; none (single-column line PK, all-key junctions). No schema change.
4. **3NF:** Resolve label_name → attack_phase by adding `attack_phase` and `attack_label`; junctions reference `label_id`.
5. **Final set:** `attack_phase`, `attack_label`, `labeled_line`, `labeled_line_label`, `labeled_line_rule`. ETL: seed phases and labels from taxonomy, load lines from staging, then explode JSON into the two junction tables using the same dependency order as the DDL.
