# Audit Log Findings - apache_error_log (intranet_server)

Source: `russellmitchell/gather/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error_log.2` (35 lines, Apache error log format).
Labels: `russellmitchell/labels/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error_log.2` (35 labeled lines).
Analysis notebook: `notebooks/02_explore_apache_error.ipynb`.
Target table: `http_events` (9 columns, 35 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued field:** The `labels` column stores a list of attack-phase tags per record (e.g. `[attacker_http, foothold, dirb]`). This is a 1NF violation - multiple distinct values packed into a single cell.

**Repeating groups:** The `rules` column is a nested dictionary mapping each label to a list of matched signatures (e.g. `{"dirb": ["attacker.foothold.apache.error.dirb"]}`). Both `labels` and `rules` violate 1NF by storing collections in a single field.

**1NF status: violated.** `labels` (array) and `rules` (nested dict) need to be unpacked. In the `http_events` table these are stored as `TEXT[]` and `JSONB` respectively, which PostgreSQL supports natively but which still represent denormalized collections.

### 2NF Check

The raw table uses a single-column surrogate primary key (`http_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

**Transitive dependency:** The `log_level` field encodes two distinct attributes - the Apache module (e.g. `authz_core`, `php7`, `negotiation`) and the severity level (e.g. `error`). This results in a dependency chain `http_event_id -> log_level -> {module, severity}`, which is a 3NF violation.

**3NF status: violated.** Resolution direction: split `log_level` into separate `module VARCHAR` and `severity VARCHAR` columns during normalization.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `http_event_id` | all other attributes | Surrogate PK. |
| FD2 | `event_id` (line_number) | all other attributes | Each log line is unique. Candidate key. |
| FD3 | `log_level` | `module`, `severity` | The composite field determines both sub-components (3NF violation). |
| FD4 | `client_ip` | constant `172.19.131.174` | All 35 labeled events share a single attacker IP. Trivial (only one value). |

---

## 2. Field-by-Field Summary

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---|---|---|
| `event_id` | 35/35 | 35 | Original 1-based line number; candidate key |
| `event_timestamp` | 35/35 | 35 | Microsecond precision; parsed from raw Apache format |
| `log_level` | 35/35 | 3 | Composite `module:severity`; see 3NF violation above |
| `client_ip` | 35/35 | 1 | Always `172.19.131.174`; fits PostgreSQL `INET` type |
| `message` | 35/35 | 35 | Free text; variable length exceeding 255 chars; stored as `TEXT` |

### Multi-valued fields (1NF violations)

| Field | Present | Notes |
|---|---|---|
| `labels` (→ `http_event_category`) | 35/35 | Array of attack-phase tags. Minimum 2 labels per record. `attacker_http` and `foothold` always co-occur. Stored as `TEXT[]` in PostgreSQL, `JSON` in MySQL. |
| `rules` (→ `http_signature_matches`) | 35/35 | Nested dict mapping label → list of signature strings. Stored as `JSONB` in PostgreSQL for indexing support, `JSON` in MySQL. |

### Derived / generated fields

| Field | Notes |
|---|---|
| `http_event_id` | Auto-incrementing surrogate PK; not present in raw log |
| `created_at` | Insert timestamp; generated at load time |

---

## 3. log_level Distribution

| log_level | Count | Module | Severity |
|---|---|---|---|
| `authz_core:error` | - | authz_core | error |
| `php7:error` | - | php7 | error |
| `negotiation:error` | - | negotiation | error |

All observed records carry severity `error`. Module encodes the Apache subsystem that generated the event. Longest observed value is `negotiation:error` (18 chars); `VARCHAR(50)` provides sufficient headroom.

---

## 4. Attack Events (Ground Truth Labels)

All 35 records are labeled - this file is 100% attack traffic. Every line represents attacker activity from IP `172.19.131.174` against the intranet server.

**Attack tool signatures observed:**

| Label | Count | Attack Stage | Description |
|---|---|---|---|
| `attacker_http` | 35 | Foothold | All records flagged as attacker HTTP traffic |
| `foothold` | 35 | Foothold | All records represent foothold-phase activity |
| `dirb` | ~most | Reconnaissance | Directory brute-force scanning (dirb tool) |
| `wpscan` | subset | Reconnaissance | WordPress vulnerability scanning |

**Structural co-occurrence:** `attacker_http` and `foothold` appear on every record. No single-label records exist - every line carries at least 2 labels. This structural co-occurrence should inform the normalized label table design.

**Attack sequence summary:** The attacker performed directory enumeration (`dirb`) and WordPress vulnerability scanning (`wpscan`) against the intranet server, all originating from a single IP.

---

## 5. Key Findings for Schema Design

1. **Single attacker IP across all records:** `172.19.131.174` is the sole `client_ip` in every labeled event. Storing as `INET` supports future indexing and cross-host join queries.

2. **1NF violations in `labels` and `rules`:** Both fields store collections per row. Stored as `TEXT[]` and `JSONB` in PostgreSQL; a fully normalized design would use a junction table for labels and a separate signatures table for rules.

3. **No single-label records:** Every record carries at least 2 labels (`attacker_http` + `foothold` always co-occur). Label co-occurrence is structural, not incidental, and should be reflected in any normalized label table design.

4. **`log_level` encodes two attributes (3NF violation):** The field combines module and severity. A normalized design would split into `module VARCHAR` and `severity VARCHAR` columns.

5. **Two attack tool signatures:** `dirb` (directory brute-force) and `wpscan` (WordPress scanning) are the two distinct attack tools detected. These map to separate detection signatures in the `rules` field.

6. **Merge with other HTTP event sources:** This Apache error log covers the intranet server's reconnaissance phase. Future normalization should combine with access logs and other server HTTP events using a `host_id` FK discriminator in the final `http_events` table.

---

## 6. DDL for Raw Loading

9 columns. The `labels` and `rules` fields store collections as-is (1NF violations - normalization unpacks them).

```sql
-- PostgreSQL
CREATE TABLE http_events (
    http_event_id          SERIAL PRIMARY KEY,
    event_id               INTEGER NOT NULL,
    event_timestamp        TIMESTAMP,
    log_level              VARCHAR(50),
    client_ip              INET,
    message                TEXT,
    http_event_category    TEXT[],
    http_signature_matches JSONB,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE http_events (
    http_event_id          INT AUTO_INCREMENT PRIMARY KEY,
    event_id               INT NOT NULL,
    event_timestamp        DATETIME,
    log_level              VARCHAR(50),
    client_ip              VARCHAR(45),
    message                TEXT,
    http_event_category    JSON,
    http_signature_matches JSON,
    created_at             DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Notes for Normalization Phase

1. **1NF violation (`labels`/`http_event_category`):** The array column packs multiple attack-phase tags into a single field. Normalization should create a `http_event_labels` junction table with `(http_event_id, label)` rows.

2. **1NF violation (`rules`/`http_signature_matches`):** The nested dict packs label-to-signature mappings into a single field. Normalization should create a `http_event_signatures` table with `(http_event_id, label, signature)` rows.

3. **3NF violation (`log_level` → `module`, `severity`):** The composite `module:severity` field should be split into separate `module VARCHAR` and `severity VARCHAR` columns during normalization.

4. **Single attacker IP:** Since all 35 labeled records share one IP, `client_ip` carries no discriminatory power within this file. It becomes meaningful only in the combined multi-host table for cross-source correlation.

5. **`event_id` as candidate key:** The original log line number (`event_id`) is unique across all 35 records and serves as a natural candidate key. The surrogate `http_event_id` is retained for FK reference stability.

6. **Merge with other HTTP logs:** This file covers the intranet server's Apache error log for the reconnaissance phase. It should be combined with access logs and other server HTTP sources in the final `http_events` table, using a `host_id` FK discriminator to distinguish source servers.