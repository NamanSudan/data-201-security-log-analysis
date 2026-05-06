# HTTP Access Log Findings - intranet_server

Source: `russellmitchell/gather/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access_log.2` (Apache Combined Log Format).
Labels: `russellmitchell/labels/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access_log.2` (labeled lines, JSON Lines format).
Analysis notebook: `notebooks/03_explore_apache_access.ipynb`.
Target table: `http_access_events` (15 columns, labeled records only).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued fields:** The `labels` column stores a list of attack-phase tags per record (e.g. `[attacker_http, foothold, wpscan]`). This is a 1NF violation - multiple distinct values packed into a single cell. The `rules` column compounds this: it is a nested dict mapping each label to a list of matched signatures. Both fields store collections where atomic values are required.

**Split URL fields:** `url_path` and `query_string` are correctly split from `url`, which is good 1NF practice - the full URL is not left as a single multi-part blob.

**1NF status: violated** in `labels` (array) and `rules` (nested dict). Stored as `TEXT[]` and `JSONB` in PostgreSQL; a fully normalized design would use junction tables. Same pattern as `labels` and `rules` in the companion intranet audit log findings (DAT-48).

### 2NF Check

The table uses a single-column surrogate primary key (`http_access_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

Transitive dependencies identified:

| Determinant | Dependent(s) | Notes |
|---|---|---|
| `url` | `url_path`, `query_string`, `decoded_command` | All URL-derived fields are fully determined by the raw URL. |
| `query_string` | `decoded_command` | The base64-decoded webshell command is entirely determined by the `wp_meta` query parameter. Computed column. |
| `client_ip` | attack context | All labeled records share the same attacker IP. In a multi-host dataset, `client_ip` could determine a host entity. |

**3NF status: `decoded_command` is a computed derived field** and could be considered a transitive dependency through `query_string`. Acceptable to store denormalized for query convenience, but should be flagged as derived in schema documentation.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `http_access_event_id` | all attributes | Surrogate PK. |
| FD2 | `event_id` (line number) | all attributes | Each line number uniquely identifies one log entry within this file. Candidate key. |
| FD3 | `url` | `url_path`, `query_string`, `decoded_command` | The full URL determines all its derived sub-fields. |
| FD4 | `query_string` | `decoded_command` | The webshell command is fully determined by the base64-encoded `wp_meta` query parameter. |

---

## 2. Field-by-Field Summary

### Core fields

| Field | Notes |
|---|---|
| `http_access_event_id` | Surrogate PK, auto-incremented at insert time. |
| `event_id` | Original line number from the raw Apache log file. Candidate key within this file. |
| `event_timestamp` | Parsed from `[DD/Mon/YYYY:HH:MM:SS ±ZZZZ]` format with `%d/%b/%Y:%H:%M:%S %z`. Includes timezone offset - stored as `TIMESTAMP WITH TIME ZONE`. |
| `client_ip` | IPv4 address of the requesting client. All labeled records: `172.19.131.174` (attacker). |
| `http_method` | HTTP verb (`GET`, `POST`, `HEAD`). NULL for null requests (HTTP 408). |
| `request_url` | Full raw URL including query string. Contains base64-encoded webshell commands in `wp_meta` parameter for webshell records. |
| `url_path` | Path component only, split from `request_url` on `?`. NULL for null requests. Enables indexing on path without query string noise. |
| `query_string` | Query string component, split from `request_url`. NULL when no `?` is present. |
| `status_code` | 3-digit HTTP response code, cast to integer. |
| `bytes_sent` | Response size in bytes. NULL (not 0) where the raw log records `-` - no response body sent. |
| `decoded_command` | Base64-decoded shell command from the `wp_meta` query parameter. NULL for all non-webshell records. Derived/computed column. |
| `request_type` | `'normal'` for standard HTTP requests; `'null_request'` for HTTP 408 (client connected but sent no data). |
| `http_access_event_category` | Array of attack-phase labels (1NF violation - stored as `TEXT[]`). |
| `http_access_signature_matches` | Nested dict of matched detection signatures per label (1NF violation - stored as `JSONB`). |

### Parsing strategy

| Raw log field | Renamed column | Notes |
|---|---|---|
| Group 1 - first token | `client_ip` | IPv4 address; no port in access log |
| Group 2 - `[DD/Mon/YYYY:HH:MM:SS ±ZZZZ]` | `event_timestamp` | Parsed with `%d/%b/%Y:%H:%M:%S %z` |
| Group 3 - HTTP verb | `http_method` | `GET`, `POST`, `HEAD`, etc. NULL for null requests |
| Group 4 - full request path + query string | `request_url` | May contain base64-encoded webshell commands in `wp_meta` |
| Group 5 - `HTTP/1.x` | `protocol` | NULL for null requests |
| Group 6 - 3-digit integer | `status_code` | Cast to `int` |
| Group 7 - integer or `-` | `bytes_sent` | `-` converted to NULL |
| Split from `url` on `?` | `url_path` | Path only, no query string |
| Split from `url` on `?` | `query_string` | NULL if no `?` present |
| `decode_wp_meta(url)` | `decoded_command` | Base64-decoded `wp_meta` parameter for webshell records |
| Derived | `request_type` | `'normal'` or `'null_request'` |

Two regex patterns handle the two log line formats:
- **Normal:** Apache Combined Log Format - `IP - - [timestamp] "METHOD /path HTTP/version" status bytes`
- **Null request:** `IP - - [timestamp] "-" 408 -` - client connected but sent no request data

---

## 3. Label Distribution

8 attack-phase label categories across all labeled records. The `labels` and `rules` fields belong to the annotation layer (DAT-48 equivalent) and carry multi-valued fields that are 1NF violations in the raw table.

| Label | Count | Category |
|---|---|---|
| `attacker_http` | (most frequent) | General attacker HTTP activity |
| `dirb` | high | Directory brute-force scanning |
| `wpscan` | high | WordPress vulnerability scanning |
| `foothold` | moderate | Initial foothold establishment |
| `service_scan` | moderate | Service/port scanning |
| `webshell_cmd` | low | Command execution via uploaded web shell |
| `webshell_upload` | low | Upload of malicious web shell |
| `escalate` | low | Privilege escalation attempts |

Most records carry 2–3 labels simultaneously (e.g. `[attacker_http, foothold, wpscan]`). Single-label records are useful for validating individual detection signatures in isolation.

### Signature → label mapping

| Label | Example signatures |
|---|---|
| `attacker_http` | `attacker.attacker_http` |
| `dirb` | `attacker.dirb` |
| `wpscan` | `attacker.wpscan` |
| `foothold` | `attacker.foothold` |
| `service_scan` | `attacker.service_scan` |
| `webshell_cmd` | `attacker.webshell_cmd` |
| `webshell_upload` | `attacker.webshell_upload` |
| `escalate` | `attacker.escalate` |

---

## 4. Attack Phases (Ground Truth Labels)

All labeled records originate from a single attacker IP: `172.19.131.174`. The access log captures the full HTTP kill chain from initial reconnaissance through to privilege escalation.

- **Reconnaissance (`service_scan`, `wpscan`, `dirb`):** Initial phase. The attacker scanned for open services, then ran wpscan against the WordPress installation, followed by dirb directory brute-forcing. dirb produces a high volume of 404 responses from the same IP in a short window.

- **Foothold (`foothold`, `webshell_upload`):** The attacker identified an upload-capable endpoint and uploaded a malicious web shell. `webshell_upload` records show the specific POST requests and target paths used.

- **Execution (`webshell_cmd`):** Commands were issued through the uploaded web shell via GET requests to the shell URL with base64-encoded commands in the `wp_meta` query parameter. The `decoded_command` column captures these in plaintext. Commands include system enumeration and file operations consistent with post-exploitation.

- **Escalation (`escalate`):** Privilege escalation attempts appear as a subset of webshell command records, cross-referencing with the intranet audit log (`su` and `sudo` events from the same timestamp window).

---

## 5. DDL for Raw Loading

15 columns. `labels` and `rules` are stored as `TEXT[]` and `JSONB` respectively (1NF violations accepted for this raw table). A fully normalized design would use junction tables.

```sql
-- PostgreSQL
CREATE TABLE http_access_events (
    http_access_event_id          SERIAL PRIMARY KEY,
    event_id                      INTEGER NOT NULL,
    event_timestamp               TIMESTAMP WITH TIME ZONE,
    client_ip                     INET,
    http_method                   VARCHAR(10),
    request_url                   TEXT,
    url_path                      TEXT,
    query_string                  TEXT,
    status_code                   SMALLINT,
    bytes_sent                    INTEGER,
    decoded_command               TEXT,
    request_type                  VARCHAR(20),
    http_access_event_category    TEXT[],
    http_access_signature_matches JSONB,
    created_at                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE http_access_events (
    http_access_event_id          INT AUTO_INCREMENT PRIMARY KEY,
    event_id                      INT NOT NULL,
    event_timestamp               DATETIME,
    client_ip                     VARCHAR(45),
    http_method                   VARCHAR(10),
    request_url                   TEXT,
    url_path                      TEXT,
    query_string                  TEXT,
    status_code                   SMALLINT,
    bytes_sent                    INT,
    decoded_command               TEXT,
    request_type                  VARCHAR(20),
    http_access_event_category    JSON,
    http_access_signature_matches JSON,
    created_at                    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Notes for Normalization Phase

1. **1NF violations (`labels` and `rules`):** Both fields store collections per row. Stored as `TEXT[]` and `JSONB` in PostgreSQL for convenience. A fully normalized schema would use junction tables: `http_access_event_labels (event_id, label)` and `http_access_event_signatures (event_id, label, signature)`. Same pattern as the companion audit log findings.

2. **`decoded_command` is a computed column:** It is derived by base64-decoding the `wp_meta` query parameter. It should be stored for query convenience but flagged as derived. Could alternatively be computed as a generated column or view.

3. **`bytes_sent` NULL vs. 0:** The raw log uses `-` when no bytes were sent. These are correctly converted to NULL, not 0. NULL should be preserved in the database to distinguish "no response body" from a legitimate zero-byte response.

4. **`client_ip` as `INET` type:** Stored as PostgreSQL `INET` / MySQL `VARCHAR(45)` to support future indexing, range queries, and multi-host comparisons. All current labeled records share the same attacker IP (`172.19.131.174`).

5. **URL fields decomposition:** `request_url` preserves the full raw URL. `url_path` and `query_string` are pre-split derived columns retained for indexing and filtering convenience. Indexing on `url_path` alone avoids query string noise for path-based analysis.

6. **`request_type` discriminator:** The `'null_request'` flag isolates HTTP 408 records where the client connected but sent no data. These have NULL `method`, `url_path`, `query_string`, and `decoded_command`. Useful for detecting connection probing or slow-loris style patterns.

7. **Merge with access log labels (DAT-48):** The annotation file covers the same log as the raw file. The join is on `line` number. The merged `df_merged` table is the definitive source for `http_access_events` - all 15 columns come from this join.

8. **Cross-reference with `audit_events_intranet_raw`:** The `escalate`-labeled access log records align by timestamp with the `su` and `sudo` audit events in `audit_events_intranet_raw` (lines 1860–1868). The attacker IP `172.19.131.174` also appears in 3 `USER_LOGIN` audit events. These two tables should be joined on timestamp and IP for full kill-chain reconstruction.