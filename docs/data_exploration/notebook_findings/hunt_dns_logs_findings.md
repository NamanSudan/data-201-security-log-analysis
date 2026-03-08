# DNS Log Findings - inet-firewall/dnsmasq.log

Source: `russellmitchell/gather/inet-firewall/logs/dnsmasq.log` (275,900 lines, dnsmasq syslog format).
Labels: `russellmitchell/labels/inet-firewall/logs/dnsmasq.log` (54,035 labeled lines).
Analysis notebook: `notebooks/06_explore_dnsmask_logs.ipynb`.
Target table: `dns_events` (this file contributes 275,900 events; labels map into `attack_labels` during normalization).

Both the gather and labels paths refer to the same logical log: raw lines from `gather/.../dnsmasq.log` and label records from `labels/.../dnsmasq.log` join on line number and build the same raw → normalized tables.

---

## 1. Normalization Analysis

### 1NF Check

**Composite field (raw dnsmasq.log):**
The log line after the syslog header is a single message string that embeds multiple attributes. Examples:
- `query[A] <domain> from <client_ip>`
- `forwarded <domain> to <upstream_ip>`
- `reply <domain> is <result>` or `reply <domain> is <CNAME>`
- `cached <domain> is <result>`
- `nameserver 127.0.0.1 refused to do a recursive query`
- `failed` (single occurrence)

So action type, query type (when present), domain, client IP, upstream IP, and reply/cache result are packed into one blob. This is a 1NF violation if stored as one column. Resolution: retain raw message; parse into atomic columns (event_action, query_type, domain, client_ip, upstream_ip, reply_value) during normalization/ETL.

**Multi-valued fields (labels file):**
Each labeled record contains:
- `labels`: an **array** of tags (e.g. `["dnsteal", "attacker", "dnsteal-received"]`)
- `rules`: a **nested dict** mapping label → list of matched signatures (e.g. `{"dnsteal": ["dnsteal.domain.match"], "dnsteal-received": ["dnsteal.domain.received"]}`)

These are 1NF violations. In the planned normalized design, these unpack into separate rows in `attack_labels` linked to the parent event.

**Repeating groups:** None (no phone1/phone2-style columns).

**1NF status: violated.**

### 2NF Check

Raw loading uses a single-column surrogate primary key (`dns_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

**Transitive dependency (message action determines schema):**
The **message action** (query, forwarded, reply, cached, nameserver, failed) determines which sub-fields can be parsed from the rest of the line:
- `query` lines: optional `[A]`/`[TXT]`/`[AAAA]`, domain, `from <client_ip>`
- `forwarded` lines: domain, `to <upstream_ip>`
- `reply` / `cached` lines: domain, `is <result>` (IP, `<CNAME>`, or CNAME target with IPs)
- `nameserver` lines: free text (e.g. "127.0.0.1 refused to do a recursive query")
- `failed` lines: no further structure

So `dns_event_id` → event_action → populated field set. This is analogous to the audit log finding (`type` → field set).

**3NF status: violated.** Resolution direction: event_type or event_action column and type-specific parsed columns (or subtype tables) in the final 3NF schema; or retain a single `dns_events` table with optional parsed columns and document the dependency in the normalization report.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `dns_event_id` | all other attributes | Surrogate PK. |
| FD2 | `line_number` | all other attributes | Each log line is unique. Candidate key. |
| FD3 | event_action (message prefix) | populated field set | Action determines which attributes can be parsed (3NF violation). |
| FD4 | (client_ip, domain, timestamp) | session/flow grouping | Meaningful for correlating query → forwarded → reply triples and for grouping exfiltration by client. |

---

## 2. Field-by-Field Summary (dnsmasq.log)

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---:|---:|---|
| `line_number` | 275900/275900 | 275900 | 1-based line number; candidate key |
| `event_timestamp` | 275900/275900 | ~many | Syslog format: "Mon DD HH:MM:SS" (no year in raw; infer from log context, e.g. 2022-01-21) |
| `host` | 275900/275900 | 1 | Always "dnsmasq" in this file |
| `process` | 275900/275900 | 1 | "dnsmasq[3468]" (process name + pid) |
| `message` | 275900/275900 | ~many | Free text; must be `TEXT` |

### Parsed sub-fields (analysis-only; not in raw DDL)

Keep raw `message` in the raw table; parsing into atomic columns is a normalization/ETL choice.

| Field | Present | Notes |
|---|---:|---|
| `event_action` | 275900/275900 | First token: query, forwarded, reply, cached, nameserver, failed |
| `query_type` | query lines only | Optional token after query, e.g. [A], [TXT], [AAAA]; NULL for non-query |
| `domain` | query, forwarded, reply, cached | Queried or resolved domain; very long for DNSteal (subdomain-encoded data) |
| `client_ip` | query only | "from &lt;IP&gt;"; e.g. 10.143.0.103, 172.19.130.4 |
| `upstream_ip` | forwarded only | "to &lt;IP&gt;"; e.g. 192.168.231.254 |
| `reply_value` | reply, cached | "is &lt;IP&gt;", "is &lt;CNAME&gt;", or "is &lt;CNAME&gt;" plus follow-up lines with resolved IPs |

### Multi-valued fields (labels file)

| Field | Present | Notes |
|---|---|---|
| `labels` (→ `dns_event_category`) | 54035/275900 | Array of attack-phase tags. Labeled records have `["dnsteal", "attacker", "dnsteal-received"]`. Stored as TEXT[] (PostgreSQL) or JSON (MySQL) in raw load. |
| `rules` (→ `dns_signature_matches`) | 54035/275900 | Nested dict mapping label → list of signature strings (e.g. dnsteal.domain.match, dnsteal.domain.received). Stored as JSONB (PostgreSQL) or JSON (MySQL). |

---

## 3. Event Type / Message Distribution

Message action (first token after `dnsmasq[pid]: `) drives event semantics:

| Action | Count | % | Notes |
|---|---:|---:|---|
| reply | 99,406 | 36.0% | Resolution result (IP, CNAME, or CNAME target IPs) |
| query | 81,277 | 29.5% | Client query (type A/TXT/AAAA, domain, from client_ip) |
| forwarded | 57,960 | 21.0% | Upstream forward (domain, to upstream_ip) |
| cached | 25,763 | 9.3% | Cache hit (domain, is result) |
| nameserver | 11,493 | 4.2% | Nameserver status (e.g. "127.0.0.1 refused to do a recursive query") |
| failed | 1 | &lt;0.1% | Single failure line |

A single DNS resolution often produces multiple log lines: one query, one forwarded, one or more reply (or cached). So event counts do not equal "number of queries"; correlation by (timestamp, domain, client_ip) groups related events.

---

## 4. Attack Events (Ground Truth Labels)

54,035 labeled lines correspond to **DNS exfiltration (DNSteal)**. Labels and rules:

- **Labels:** `dnsteal`, `attacker`, `dnsteal-received` (all three co-occur on every labeled line).
- **Rules:** `dnsteal.domain.match`, `dnsteal.domain.received` — detection is based on domain matching the exfiltration pattern (e.g. subdomains of `kennedy-mendoza.info` used to encode stolen data).

**Label distribution (54,035 labeled records):**
- `dnsteal`: 54,035
- `attacker`: 54,035
- `dnsteal-received`: 54,035

**Context (from data_scope_and_findings.md):** Exfiltration phase runs until 13:50; DNSteal encodes stolen data in subdomain queries. The exfil domain pattern in the log is `*.customers_2017.xlsx.email-19.kennedy-mendoza.info` (long base64-like subdomain labels). Client IP for these queries is **10.143.0.103**. Each query typically produces three log lines (query, forwarded, reply), so labeled line numbers span both "query" and "forwarded"/"reply" actions; the same logical exfiltration event can appear on multiple consecutive raw lines with the same labels.

**Unlabeled traffic:** 221,865 lines are normal DNS (ClamAV updates, general resolution, nameserver messages, cache hits). These provide baseline for anomaly detection.

---

## 5. Key Findings for Schema Design

1. **Single raw log, two paths:** Both `russellmitchell/gather/inet-firewall/logs/dnsmasq.log` and `russellmitchell/labels/inet-firewall/logs/dnsmasq.log` refer to the same logical log. The gather file holds raw lines; the labels file holds line-number-keyed labels. ETL joins on line number to produce one raw table (e.g. `dns_events_raw`) and then normalizes into `dns_events` and `attack_labels`.

2. **Message is composite:** The `message` field embeds action, query type, domain, client_ip, upstream_ip, and reply value. Raw table keeps it as one TEXT column; normalization can split into `event_action`, `query_type`, `domain`, `client_ip`, `upstream_ip`, `reply_value`.

3. **1NF violations in `labels` and `rules`:** Same pattern as other findings. Store as TEXT[]/JSONB (PostgreSQL) and JSON (MySQL) in raw load; normalize to `attack_labels` (and optionally signature tables).

4. **3NF violation (event_action → field set):** Message action determines which parsed sub-fields exist. Normalization can introduce `event_action` (or `event_type`) and type-specific columns or subtype tables.

5. **Exfiltration traffic is a small subset:** 54,035 / 275,900 ≈ 19.6% of lines are labeled; the rest are legitimate DNS. Correlation with VPN/Apache/auth logs uses client IP 10.143.0.103 (internal host performing exfiltration) and time window (through 13:50 on the log date).

6. **No year in syslog timestamp:** Raw timestamp is "Mon DD HH:MM:SS". Year must be inferred from scenario (e.g. 2022) and stored in `event_timestamp` at load time.

---

## 6. DDL for Raw Loading (dnsmasq.log + labels)

This raw-load shape follows the project rule **Raw = truly raw**:
- Keep `message` as a single TEXT blob (1NF violation when it embeds multiple attributes).
- Do **not** store message-parsed sub-fields (event_action, query_type, domain, client_ip, upstream_ip, reply_value) in the raw DDL.
- Multi-valued `labels` and nested `rules` from the label file are stored as-is (1NF violations; normalization unpacks them).
- `host` and `process` can be stored as parsed from the syslog header for convenience; alternatively fold into `message` if strict single-blob per line is desired. Below they are separate columns to match common syslog parsing.

```sql
-- PostgreSQL
CREATE TABLE dns_events_raw (
    dns_event_id            SERIAL PRIMARY KEY,
    line_number             INTEGER NOT NULL,
    event_timestamp         TIMESTAMP WITH TIME ZONE,
    host                    VARCHAR(50),
    process                 VARCHAR(100),
    message                 TEXT NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE dns_events_raw (
    dns_event_id            INT AUTO_INCREMENT PRIMARY KEY,
    line_number             INT NOT NULL,
    event_timestamp         DATETIME,
    host                    VARCHAR(50),
    process                 VARCHAR(100),
    message                 TEXT NOT NULL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Notes for Normalization Phase

1. **Unpack labels/rules to `attack_labels`:** Each (event, label) becomes one row; each (event, label, signature) becomes one row if signatures are modeled separately.

2. **Parse message into atomic columns:** Derive `event_action`, `query_type`, `domain`, `client_ip`, `upstream_ip`, `reply_value` from `message` for analytics. Optionally keep `message` for display and audit.

3. **Infer year for event_timestamp:** Set year (e.g. 2022) from scenario metadata when converting "Mon DD HH:MM:SS" to full timestamp.

4. **Correlate query → forwarded → reply:** Group by (timestamp, domain, client_ip) or use a session/flow identifier if building a normalized fact table of "resolutions" rather than one row per log line.

5. **Cross-log correlation:** Exfiltration client 10.143.0.103 can be correlated with other logs (e.g. audit, Apache) by IP and time. The attacker’s VPN-assigned IP (172.19.131.174) appears in other logs; 10.143.0.103 is the host where DNSteal is running (intranet host exfiltrating via DNS).
