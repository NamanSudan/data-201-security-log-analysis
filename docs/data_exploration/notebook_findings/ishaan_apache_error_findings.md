# Audit Log Findings - apache_error_log (intranet_server)

Source: `russellmitchell/gather/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error_log.2` (35 lines, Apache error log format).
Labels: `russellmitchell/labels/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error_log.2` (35 labeled lines).
Analysis notebook: `notebooks/02_explore_apache_error.ipynb`.
Target table: `http_errors` (14 columns, 37 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued field:** The `message_raw` column packs all human-readable detail into a single text blob, including the target file path, error context, and sometimes a referer URL. Extracting `target_path` and `referer` as separate columns partially resolves this, but the `message` column still contains freeform text that cannot be fully atomized without type-specific parsing.

**Repeating groups:** None. No field1, field2, field3 patterns.

**1NF status: partially violated.** `message_raw` packs multiple values. The parsed `target_path` and `referer` extractions are 1NF remediation steps.

### 2NF Check

The raw table uses a single-column surrogate primary key (`http_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

**Transitive dependencies identified:**

| Determinant | Dependent(s) | Notes |
|---|---|---|
| `module` | `level`, `error_code` pattern | Each Apache module produces a characteristic severity level and error code. `authz_core` always produces AH01630 at `error` level; `php7` produces no AH code; `negotiation` produces AH00687. Structural FD: module → {level, error_code_pattern}. |
| `error_code` | message template prefix | AH01630 always means "client denied by server configuration"; AH00687 always means negotiation failure. The specific file path varies, but the error description prefix is fully determined by `error_code`. |

**3NF status: violated.** The module → error_code and error_code → message_template chains are transitive dependencies through non-key attributes.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `row_id` | all attributes | Surrogate PK. |
| FD2 | `line_number` | all attributes | Each log line is unique within this file. Candidate key. |
| FD3 | `error_code` | `message` prefix | The AH##### code determines the human-readable error description prefix. The path suffix varies per event. |
| FD4 | `module` | `level`, `error_code` range | Structural FD: module determines which severity levels and error codes are possible. |
| FD5 | `client_ip` | probe intent | Dataset-specific: the single source IP `172.19.131.174` is the known attacker. Not a general schema FD. |

---

## 2. Field-by-Field Summary

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---|---|---|
| `row_id` | 37/37 | 37 | Surrogate PK. |
| `line_number` | 37/37 | 37 | Original 1-based line number; candidate key. |
| `timestamp` | 37/37 | 37 | Microsecond precision; parsed from raw Apache error log format to `TIMESTAMPTZ`. |
| `raw_timestamp` | 37/37 | 37 | Raw unparsed timestamp string, e.g. `Mon Jan 24 03:57:26.696483 2022`. Preserved as `VARCHAR(40)`. |
| `module` | 37/37 | 4 | Apache module that generated the error: `authz_core`, `php7`, `negotiation`, `autoindex`. |
| `level` | 37/37 | 1 | Severity level. Always `error` in this log. |
| `pid` | 37/37 | varies | Apache worker process ID. Cast to `INT`. |
| `client_ip` | 37/37 | 1 | Always `172.19.131.174`. Fits PostgreSQL `INET` type. |
| `client_port` | 37/37 | 26 | Client-side TCP port. 26 distinct ports across 37 entries — sequential allocation pattern consistent with a single scanning process. Cast to `INT`. |
| `error_code` | 18/37 | 3 | AH##### Apache error code. NULL for `php7` entries (script-not-found and PHP fatal errors carry no AH code). Values: AH01630, AH00687, AH01276. |
| `message_raw` | 37/37 | 37 | Full unparsed message body. Multi-valued — packs target path, error context, and optional referer. Stored as `TEXT`. |
| `message` | 37/37 | 37 | Cleaned message: `message_raw` with AH##### prefix and referer suffix stripped. Stored as `TEXT`. |
| `target_path` | 37/37 | 37 | File or directory path extracted from the message body. All paths are under `/var/www/intranet.smith.russellmitchell.com/`. |
| `referer` | 26/37 | 1 | Referer URL extracted from message suffix. NULL for first 11 lines (blind initial probes); `https://intranet.smith.russellmitchell.com` for the remaining 26 (second-stage targeted probes). |

### module distribution

| module | Count | Error codes produced | Notes |
|---|---|---|---|
| `authz_core` | 6 | AH01630 | Access denied — htaccess, htpasswd, server-status probes |
| `php7` | 19 | none | Script not found or PHP fatal error |
| `negotiation` | 11 | AH00687 | Content negotiation failure — wp-* files, xmlrpc, functions |
| `autoindex` | 1 | AH01276 | Directory listing forbidden — wp-content/uploads/ |

---

## 3. Attack Probe Phases

The 37 errors split cleanly into two phases based on the presence of a referer header.

**Phase 1 — Blind initial probes (lines 1–11, no referer):** Automated scan with no prior site knowledge. Probes: `.hta*`, `.htaccess*`, `.htpasswd*` (authz_core AH01630), `admin.php`, `info.php`, `phpinfo.php`, `server-status`, wp-core files, `xmlrpc`.

**Phase 2 — Targeted second-stage probes (lines 12–37, referer present):** After the attacker browsed the site, probes focus on WordPress exploitation vectors: `searchreplacedb2.php`, `emergency.php`, `timthumb.php` variants across 7 theme/plugin locations, `wp-content/uploads/` directory listing, and WordPress theme functions. Line 27 is the highest-signal entry: a PHP Fatal error (`Call to undefined function get_header()`) confirms the server is running WordPress with the "Go" theme and that the attacker successfully triggered server-side theme code execution.

| Phase | Lines | Referer | Probe types |
|---|---|---|---|
| Phase 1 (blind scan) | 1–11 | None | htaccess, admin.php, info, server-status, wp-core, xmlrpc |
| Phase 2 (targeted) | 12–37 | `https://intranet.smith.russellmitchell.com` | timthumb variants, emergency.php, uploads dir, functions |

---

## 4. Key Findings for Schema Design

1. **Single-source attack burst:** All 37 errors originate from `172.19.131.174` in a ~2-minute window (03:57–03:58 UTC, 2022-01-24). No baseline normal error traffic — the log is 100% attack reconnaissance.

2. **`module` and `level` are already split:** Unlike the findings doc's original `log_level` composite field, the notebook parses `module` and `level` as separate columns from the raw `[module:level]` bracket. No 3NF split is needed at load time — it is already done in parsing.

3. **`message_raw` is the primary 1NF violation:** Packs target path, error context, and optional referer into one blob. `target_path` and `referer` are extracted as separate columns. The remaining `message` TEXT field is still freeform but cannot be further atomized without loss of information.

4. **`client_port` uniquely identifies TCP connections:** 26 distinct client ports across 37 entries. Sequential port allocation (36072, 36076, 36110, ...) is consistent with a single automated scanning process. Multiple errors per port indicate persistent connections.

5. **`error_code` is NULL for 19 of 37 rows:** All `php7` entries (script-not-found and PHP fatal errors) carry no AH code. NULL in `error_code` is a meaningful signal — it distinguishes `php7` from `authz_core`/`negotiation`/`autoindex` entries without needing to inspect `module`.

6. **Referer as phase boundary:** `referer IS NULL` isolates Phase 1 (11 blind probes); `referer IS NOT NULL` isolates Phase 2 (26 targeted probes). This single-column filter is the cleanest phase discriminator in the table.

7. **No label data in this notebook:** Unlike `ishaan_apache_error_findings.md`'s original description, the `06_explore_error_log_intranet.ipynb` notebook does not join a label file. The `http_errors` table is a raw 1:1 representation of the log. Label integration is handled separately (DAT-48 equivalent).

8. **Merge with access log (DAT-44):** The error log captures the failed subset of WPScan probes. The `http_errors` and `http_access` tables are joinable on `(client_ip, timestamp)`. Both should carry a `host_id` FK for multi-host joins.

---

## 5. DDL for Raw Loading

14 columns. Raw 1:1 representation of the Apache error log. `module` and `level` are stored as separate columns — they are parsed directly from the `[module:level]` bracket in the raw format, not derived in post-processing.

```sql
-- PostgreSQL
CREATE TABLE http_errors (
    row_id          SERIAL PRIMARY KEY,
    line_number     INT             NOT NULL,
    timestamp       TIMESTAMPTZ,
    raw_timestamp   VARCHAR(40),
    module          VARCHAR(20)     NOT NULL,
    level           VARCHAR(10)     NOT NULL,
    pid             INT,
    client_ip       INET,
    client_port     INT,
    error_code      VARCHAR(10),
    message         TEXT,
    message_raw     TEXT,
    target_path     TEXT,
    referer         TEXT
);
```

```sql
-- MySQL
CREATE TABLE http_errors (
    row_id          INT AUTO_INCREMENT PRIMARY KEY,
    line_number     INT             NOT NULL,
    `timestamp`     DATETIME(6),
    raw_timestamp   VARCHAR(40),
    module          VARCHAR(20)     NOT NULL,
    level           VARCHAR(10)     NOT NULL,
    pid             INT,
    client_ip       VARCHAR(45),
    client_port     INT,
    error_code      VARCHAR(10),
    message         TEXT,
    message_raw     TEXT,
    target_path     TEXT,
    referer         TEXT
);
```

---

## 6. Notes for Normalization Phase

1. **1NF violation in `message_raw`:** The raw message body packs target path, error context, and optional referer into one text blob. `target_path` and `referer` are extracted as separate columns at parse time. The remaining `message` TEXT field is still freeform — further atomization is not meaningful without type-specific NLP.

2. **`module` and `level` are already split at parse time:** No 3NF remediation is needed for these columns — the composite `[module:level]` bracket is parsed into two separate fields in the notebook. The 3NF violation noted above refers to the transitive dependency module → error_code, which would require a module lookup table to fully resolve.

3. **`error_code` → message prefix lookup table:** AH01630 always maps to "client denied by server configuration"; AH00687 always maps to "content negotiation failure"; AH01276 always maps to "cannot serve directory". A normalized design would extract these to an `apache_error_codes` lookup table with `(error_code, description)`.

4. **`client_port` retained for connection-level analysis:** Port reuse across errors reveals TCP connection persistence — multiple errors per port mean the scanner held connections open across requests. Useful for fingerprinting scanner behaviour in cross-log analysis.

5. **`raw_timestamp` preservation:** The microsecond-precision raw timestamp string is retained alongside the parsed `TIMESTAMPTZ` to preserve the original format and avoid any rounding during bulk loading.

6. **No label data in this notebook:** The `http_errors` table is a raw 1:1 representation of the log file. Label/annotation integration (attack-phase tags, signature matches) is handled in a separate notebook and produces a separate annotated table.

7. **Merge with access log (DAT-44):** This error log covers the failed subset of the WPScan scan window (03:57–03:58). The companion access log records the same requests as 403/404 responses. The `http_errors` and `http_access` tables should share a `host_id` FK and be joinable on `(client_ip, timestamp)`.
