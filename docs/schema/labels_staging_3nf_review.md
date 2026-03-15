# Review: Attack Labels Staging and 3NF Plan

Review of the staging table and 3NF normalization design for the attack labels file (see `labels_normalization_staging_to_3nf.md` and the Attack Labels section in `normalization_raw_to_3nf.md`). This review compares the plan to the **raw label files** in `russellmitchell/labels`, the **staging model and parser** (`src/models/staging/labels.py`, `src/parsers/staging/labels.py`), and **NormalizationRules.md**. Recommendations are listed for resolving issues and improving robustness.

---

## Summary

The design is **sound**: staging grain, 1NF→2NF→3NF path, and final table set are consistent with the findings in `naman_labels_findings.md`. The 3NF DDL in `sql/3nf/` matches the doc. **Raw files, parser, and model align with the plan; no data loss and no invented data** when normalization is applied as specified. The plan **complies with NormalizationRules.md** (1NF: explode arrays; 2NF: no partial dependencies; 3NF: transitive dependency resolved via lookup tables). A few changes are recommended to harden data integrity, align docs, and make ETL behavior explicit.

---

## Comparison: Plan vs. Raw Files and Staging Code

### Raw label files (`russellmitchell/labels/`)

There are **8 JSONL files** (paths verified in repo). The parser's `LABEL_FILE_CONFIG` maps each to `source_host` and `source_log` (e.g. inet-firewall/dnsmasq.log, intranet_server/access.log.2, error.log.2, audit.log, auth.log, monitoring/cpu.log, vpn/openvpn.log, internal_share/audit.log). **JSON schema (per line):** Exactly three fields: `line` (int), `labels` (array of str), `rules` (object: label → list of rule names). Sampled raw content matches the plan; `rules` keys match `labels` entries. Plan staging grain and column mapping are correct.

### Staging parser (`src/parsers/staging/labels.py`)

`LABEL_FILE_CONFIG` defines all 8 files; `source_host` and `source_log` come from config (not from JSON). Each row: `source_host`, `source_log`, `line_number` (from `obj["line"]`), `labels_json`, `rules_json`. Every non-empty line becomes one row; blank lines skipped. No data loss (raw has only these three fields). Expected staging count 61,862 if no blank lines between records.

### Staging model (`src/models/staging/labels.py`)

Table `stg_attack_label_line_raw`: `row_id` (PK), `source_host` String(30), `source_log` String(50), `line_number` Integer, `labels_json` Text, `rules_json` Text. Matches plan and parser. **Gap:** No UNIQUE on `(source_host, source_log, line_number)` in the model; add it (see Recommended Changes §1 and implementation in Checklist).

---

## NormalizationRules.md Compliance

Per **NormalizationRules.md** (DATA 201, Lecture 4/5):

- **1NF:** Staging has multi-valued `labels_json` and `rules_json`. Resolution: junction tables **labeled_line_label** and **labeled_line_rule** so each cell holds one value (one row per line–label and per line–label–rule). ✓
- **2NF:** `labeled_line` has single-column PK; junction tables have composite PKs with no non-key attributes → no partial dependencies. ✓
- **3NF:** Transitive dependency `label_name → attack_phase` resolved by **attack_phase** and **attack_label**; junctions reference `label_id`. ✓
- **Process:** Flat table → 1NF (explode) → 2NF (verify no partial deps) → 3NF (lookups). ✓

---

## Data-Loss and Invented-Data Verification

- **No data loss:** Raw → staging: all three JSON fields stored. Staging → 3NF: one **labeled_line** per staging row; one **labeled_line_label** per label in `labels_json`; one **labeled_line_rule** per (label, rule) in `rules_json`. Lookup tables (**attack_phase**, **attack_label**) are seeded from project taxonomy; every raw label string must exist in taxonomy (or a documented "unknown" policy).
- **No invented data:** Fact rows only from raw or taxonomy. **attack_phase** and **attack_label** rows come from project taxonomy only; no synthetic labels or phases.

---

## What's Working Well

- **Staging grain:** One row per labeled line with `(source_host, source_log, line_number)` as candidate key matches the 61,862 records and join to audit.
- **1NF treatment:** Replacing `labels_json` and `rules_json` with `labeled_line_label` and `labeled_line_rule` is correct; row counts (e.g. ~184,517 for line–label) match findings.
- **3NF treatment:** `attack_phase` and `attack_label` correctly resolve the external FD `label_name → attack_phase`; junctions use `label_id`.
- **DDL:** `sql/3nf/` DDL matches the doc (order, FKs, PKs, types). `labeled_line` has `UNIQUE(source_host, source_log, line_number)` for provenance.
- **ETL order:** Load order (phase → label → line → junctions) respects FKs.

---

## Recommended Changes

### 1. Add UNIQUE on staging candidate key (staging table)

**Issue:** The documented candidate key for `stg_attack_label_line_raw` is `(source_host, source_log, line_number)` and is stated as unique, but the DDL does not enforce it.

**Recommendation:** In `normalization_raw_to_3nf.md` (and any physical staging DDL), add:

```sql
UNIQUE (source_host, source_log, line_number)
```

to `stg_attack_label_line_raw`. This protects against duplicate rows if the same file is loaded twice or if the loading procedure is changed. **Also add the constraint to the SQLAlchemy model** (`src/models/staging/labels.py`) so migrations/DDL stay in sync.

---

### 2. Align findings doc staging DDL with main schema

**Issue:** In `naman_labels_findings.md` §7, the suggested staging DDL uses `VARCHAR(20)` for `source_host` and `source_log`. The main schema in `normalization_raw_to_3nf.md` uses `VARCHAR(30)` and `VARCHAR(50)` to match `stg_audit_line_raw`.

**Recommendation:** Update the findings doc to use `VARCHAR(30)` and `VARCHAR(50)` so staging DDL is consistent and joins to audit remain type-aligned. Optionally add a short note that widths are chosen to match the audit staging table.

---

### 3. Document ETL behavior for unknown labels

**Issue:** ETL assumes every label string in `labels_json` exists in `attack_label`. If a new label appears in the data that is not in the taxonomy seed, inserts into `labeled_line_label` (and `labeled_line_rule`) will fail on the FK to `attack_label`.

**Recommendation:** In `labels_normalization_staging_to_3nf.md` (e.g. in §9 ETL steps or §11 Unresolved):

- State that **all** label strings in the JSONL must exist in the seeded `attack_label` table (fail-fast behavior), **or**
- Define an "unknown" phase/label and document that any label not in the taxonomy is mapped to it (and add that to the seed list).

Pick one strategy and document it so implementers and operators know the intended behavior.

---

### 4. Document exact phase_name values for seed data

**Issue:** The doc says phase names should be "consistent (e.g. snake_case: `exfiltration`, `web_enumeration`, …)" but the taxonomy in `naman_labels_findings.md` §4 uses title case ("Exfiltration", "Web Enumeration"). Seed data and ETL must agree on the same strings.

**Recommendation:** In `labels_normalization_staging_to_3nf.md` (e.g. Step 1 or a new "Seed data" subsection), list the exact 7 `phase_name` values to use (e.g. from the findings or from `data_scope_and_findings.md`). For example:

- Either: `exfiltration`, `web_enumeration`, `initial_access`, `reconnaissance`, `privilege_escalation`, `password_cracking`, `exploitation`
- Or: `Exfiltration`, `Web Enumeration`, … (if that is the project standard)

Then refer to that list in the ETL steps so phase/label seeding is unambiguous.

---

### 5. Optional: Idempotent inserts for junction tables

**Issue:** The ETL text says "Ignore duplicates if any (composite PK will reject …)". That implies failed inserts on duplicate `(labeled_line_id, label_id)` or `(labeled_line_id, label_id, rule_name)`. Findings show no such duplicates in the current data, but re-runs or partial loads may produce them.

**Recommendation:** Document that ETL may use `INSERT ... ON CONFLICT (labeled_line_id, label_id) DO NOTHING` (and the equivalent for `labeled_line_rule`) for idempotent loads. If the design is strictly "no duplicates ever," keep current behavior but state explicitly that duplicate keys cause insert failure and are not retried.

---

### 6. Optional: Verify rule_name length for VARCHAR(120)

**Issue:** `labeled_line_rule.rule_name` is `VARCHAR(120)`. The findings list 36 rules with names like `dnsteal.domain.match` but do not report maximum length.

**Recommendation:** Either confirm in the exploration notebook (e.g. `max(len(r))` over all rule names) that 120 is sufficient, or add a short note in the DDL/doc that 120 was chosen as a safe upper bound and can be adjusted if longer rule names appear.

---

## No Change Recommended

- **labeled_line without host_id/audit_event_id:** Deferred join via `(source_host, source_log, line_number)` is documented and acceptable.
- **rule_name as string (no rule table):** Documented as optional later; keeping only `rule_name` in the junction is fine.
- **2NF "no schema change":** Correct; no partial dependencies on the line or junction keys.

---

## Checklist for implementation

- [ ] Add `UNIQUE (source_host, source_log, line_number)` to staging DDL for `stg_attack_label_line_raw` (normalization_raw_to_3nf.md and SQLAlchemy model).
- [ ] Update `naman_labels_findings.md` staging DDL to use `VARCHAR(30)` / `VARCHAR(50)` for provenance columns.
- [ ] Document unknown-label policy (fail-fast vs. "unknown" label) in the labels normalization doc.
- [ ] Add the exact list of 7 `phase_name` seed values to the labels normalization doc.
- [ ] (Optional) Document or implement `ON CONFLICT DO NOTHING` for junction inserts.
- [ ] (Optional) Confirm or document `rule_name` max length for `VARCHAR(120)`.
