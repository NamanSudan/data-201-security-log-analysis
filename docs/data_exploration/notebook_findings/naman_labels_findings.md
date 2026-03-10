# Label Files Findings - All 8 JSONL Files

Source: `russellmitchell/labels/` (8 JSONL files across 5 hosts, 61,862 records total).
Analysis notebook: `notebooks/09_explore_labels.ipynb`.
Suggested staging table: `stg_attack_label_line_raw` (61,862 rows).

---

## 1. Normalization Analysis

These are observations about the data structure, for staging and ETL design. No tables exist yet.

### 1NF Check

**Multi-valued field 1: `labels`**
Each JSONL record contains a `labels` field that is a JSON array of label strings. Observed: min 2, max 4 labels per record, mean 2.98. Distribution: 1,073 records (1.7%) have 2 labels, 60,785 records (98.3%) have 3 labels, 4 records (0.0%) have 4 labels. This is multi-valued data-a 1NF concern for staging/ETL design.

**Multi-valued field 2: `rules`**
Each JSONL record contains a `rules` field that is a JSON object mapping label names to arrays of rule names. Each label has 1 to 3 rules (observed min=1, max=3). The keys of the rules object always match the entries of the labels array (verified: 0 mismatches across all 61,862 records). This is nested multi-valued data-a 1NF concern for staging/ETL design.

**1NF observation:** Both `labels` and `rules` contain multi-valued data. If stored as TEXT blobs in a staging table, the 1NF violation is deferred to the normalization/ETL phase. Resolution direction: junction tables during normalization.

### 2NF Check

**Candidate key observed:** `(source_host, source_log, line)` is unique-verified with 0 duplicates across all 61,862 records. Each line in a given file has exactly one label record.

If a composite key were used, both `labels` and `rules` depend on the full composite (different files have different labels for any given line number), so no partial dependency exists.

**2NF observation: no partial dependencies detected.**

### 3NF Check

**Within the JSONL data fields** (`line`, `labels`, `rules`): no transitive dependency observed. No field determines another field beyond the candidate key relationship.

**External domain knowledge:** Each of the 22 label names maps to exactly one of 7 attack phases (verified deterministic: 22 labels, 0 inconsistencies). The mapping comes from the project taxonomy (`data_scope_and_findings.md`), not from the JSONL data itself. The FD `label_name -> attack_phase` is relevant for ETL design: if both `label_name` and `attack_phase` appear as columns in a normalized schema, this transitive dependency should be resolved with a lookup table.

`rule_name` does NOT determine `label_name`: 29 of 36 rules trigger multiple labels. The relationship is many-to-many.

**3NF observation:** No transitive dependency within the JSONL fields themselves. The `label_name -> attack_phase` FD is external taxonomy relevant for normalization planning.

### Preliminary Functional Dependencies

Observed from the data (no tables exist yet-these inform staging/ETL design):

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `(source_host, source_log, line)` | `labels`, `rules` | Candidate key. Verified: 0 duplicates across 61,862 records. |
| FD2 | `labels` array | `rules` dict keys | Structural constraint: rules keys always equal labels entries (0 mismatches). Not a traditional FD-an integrity constraint in the source data. |

Post-decomposition FD (for normalization planning):

| FD | Determinant | Dependent(s) | Source | Reasoning |
|---|---|---|---|---|
| FD3 | `label_name` | `attack_phase` | Project taxonomy (`data_scope_and_findings.md`) | Each of 22 labels maps to exactly 1 of 7 phases. Verified deterministic. Not present in JSONL data. |

---

## 2. Schema Overview

All 8 files share an identical JSON schema (verified: schema uniform = True).

Each JSONL line has 3 fields:
- `line` (int): line number in the corresponding raw log file. Range: 1 to 254,393.
- `labels` (list of str): attack phase tags. Always 2-4 entries.
- `rules` (dict of str to list of str): mapping of each label to the detection rules that triggered it. Rules per label: 1-3.

---

## 3. Per-File Summary

| # | Host | Log | Labeled Lines | Unique Labels | Unique Combos | Unique Rules | Line Range | Raw Lines | Coverage |
|---|------|-----|---:|---:|---:|---:|---|---:|---:|
| 1 | inet-firewall | dnsmasq.log | 54,035 | 13 | 9 | 16 | 1 - 254,393 | 275,900 | 19.6% |
| 2 | intranet_server | access.log.2 | 7,695 | 8 | 7 | 8 | 832 - 8,529 | 8,530 | 90.2% |
| 3 | intranet_server | error.log.2 | 36 | 4 | 2 | 5 | 1 - 36 | 36 | 100.0% |
| 4 | intranet_server | audit.log | 9 | 4 | 2 | 3 | 1,860 - 1,868 | 2,316 | 0.4% |
| 5 | intranet_server | auth.log | 8 | 5 | 4 | 5 | 145 - 152 | 272 | 2.9% |
| 6 | monitoring | cpu.log | 49 | 2 | 1 | 1 | 321 - 369 | 1,920 | 2.6% |
| 7 | vpn | openvpn.log | 28 | 2 | 1 | 1 | 4,331 - 4,358 | 5,537 | 0.5% |
| 8 | internal_share | audit.log | 2 | 3 | 1 | 1 | 667 - 668 | 732 | 0.3% |
| | **Total** | | **61,862** | **22** | **21** | **36** | | **295,243** | **21.0%** |

Dominant file: inet-firewall/dnsmasq.log accounts for 87.4% of all label records (54,035 of 61,862), almost entirely DNS exfiltration (attacker + dnsteal + dnsteal-received combo: 53,006 lines).

Six of eight files have fewer than 50 labeled lines. The data is heavily concentrated in dnsmasq.log (exfiltration) and access.log.2 (web enumeration).

---

## 4. Label Taxonomy (22 Labels, 7 Attack Phases)

Phase mapping from project taxonomy (`data_scope_and_findings.md`), verified deterministic.

| Phase | Labels | Label Occurrences |
|-------|--------|------------------:|
| Exfiltration | attacker (53,056), dnsteal (53,056), dnsteal-received (53,006), dnsteal-dropped (48), exfiltration-service (2) | 159,168 |
| Web Enumeration | attacker_http (7,723), dirb (4,493), wpscan (3,207) | 15,423 |
| Initial Access | foothold (8,724), attacker_vpn (28) | 8,752 |
| Reconnaissance | service_scan (455), dns_scan (414), network_scan (92), traceroute (4) | 965 |
| Privilege Escalation | escalate (82), escalated_command (10), escalated_sudo_command (10), attacker_change_user (8), escalated_sudo_session (3) | 113 |
| Password Cracking | crack_passwords (49) | 49 |
| Exploitation | webshell_cmd (44), webshell_upload (3) | 47 |
| **Total** | **22 labels** | **184,517 occurrences** |

Note: total occurrences (184,517) exceeds total rows (61,862) because each row has 2-4 labels.

---

## 5. Top Label Co-Occurrence Patterns

21 unique label combinations observed across all files.

| Combo | Count |
|-------|------:|
| attacker + dnsteal + dnsteal-received | 53,006 |
| attacker_http + dirb + foothold | 4,485 |
| attacker_http + foothold + wpscan | 3,199 |
| foothold + service_scan | 447 |
| dns_scan + foothold | 414 |
| foothold + network_scan | 92 |
| crack_passwords + escalate | 49 |
| attacker + dnsteal + dnsteal-dropped | 48 |
| attacker_http + foothold + webshell_cmd | 28 |
| attacker_vpn + foothold | 28 |
| (11 more combos with counts 1-16) | |

---

## 6. Rule Inventory (36 Rules)

| Rule | Count | Labels Triggered |
|------|------:|------------------|
| dnsteal.domain.match | 106,108 | attacker, dnsteal |
| dnsteal.domain.received | 53,006 | dnsteal-received |
| attacker.foothold.apache.access | 15,374 | attacker_http, foothold |
| attacker.dirb.time | 4,485 | dirb |
| attacker.wpscan.time | 3,199 | wpscan |
| (31 more rules with counts 3-654) | | |

29 of 36 rules trigger multiple labels. 7 rules trigger exactly 1 label. The rule-to-label relationship is many-to-many.

---

## 7. Suggested Staging DDL

Suggested schema for loading the raw JSONL data into a staging table. 6 columns. `labels_json` and `rules_json` store original JSON as TEXT blobs (multi-valued data preserved as-is; decomposition happens during ETL to 3NF). Type inference: `line_number` max observed is 254,393; fits INTEGER. `source_host` and `source_log` are derived from file paths (not in the JSONL data) to identify provenance when combining 8 files into one table.

```sql
-- PostgreSQL
CREATE TABLE stg_attack_label_line_raw (
    row_id          SERIAL PRIMARY KEY,
    source_host     VARCHAR(20) NOT NULL,
    source_log      VARCHAR(20) NOT NULL,
    line_number     INTEGER NOT NULL,
    labels_json     TEXT NOT NULL,
    rules_json      TEXT NOT NULL
);
```

```sql
-- MySQL
CREATE TABLE stg_attack_label_line_raw (
    row_id          INT AUTO_INCREMENT PRIMARY KEY,
    source_host     VARCHAR(20) NOT NULL,
    source_log      VARCHAR(20) NOT NULL,
    line_number     INT NOT NULL,
    labels_json     TEXT NOT NULL,
    rules_json      TEXT NOT NULL
);
```

---

## 8. Notes for Staging and ETL Design

1. **Multi-valued `labels` field:** The `labels` JSON array contains 2-4 label strings per record. ETL should decompose into a junction structure with one row per label per record. Same multi-valued pattern as `groups` in hosts data and `msg` in audit log data.

2. **Multi-valued `rules` field:** The `rules` JSON dict maps labels to rule arrays. ETL should decompose into a junction structure with one row per rule per label per record.

3. **Structural constraint:** The rules dict keys always match the labels array entries (0 mismatches verified). The decomposed schema should preserve this constraint via foreign keys.

4. **External FD (label_name -> attack_phase):** Each of the 22 labels maps deterministically to one of 7 attack phases (from project taxonomy, verified). When labels are decomposed, this FD should inform whether a lookup table is needed to avoid transitive dependency in the 3NF schema.

5. **Relational bridge:** The label data connects to every raw log file via `(source_host, source_log, line_number)`. The staging candidate key is `(source_host, source_log, line_number)` for this dataset. This enables label timeline reconstruction and labeled event filtering across all 8 log types.

6. **Data skew:** 87.4% of label records come from one file (dnsmasq.log). The exfiltration phase dominates. This skew should be considered in indexing strategy.

7. **Coverage variation:** Attack-labeled lines range from 0.3% (internal_share/audit.log) to 100% (intranet_server/error.log.2) of raw log lines. Overall: 21.0% of raw log lines are labeled.

8. **Derived columns in df_raw:** `source_host` and `source_log` are derived from file paths, not from the JSONL data. They are needed because 8 files with identical schema are combined into one DataFrame/table.
