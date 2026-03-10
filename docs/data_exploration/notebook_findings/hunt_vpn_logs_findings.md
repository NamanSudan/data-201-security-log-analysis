# VPN Log Findings - vpn/openvpn.log

Source: `russellmitchell/gather/vpn/logs/openvpn.log` (5,537 lines, OpenVPN server log format).
Labels: `russellmitchell/labels/vpn/logs/openvpn.log` (28 labeled lines).
Analysis notebook: `notebooks/04_explore_openvpn_logs.ipynb`.
Target table: `vpn_events` (this file contributes 5,537 events; labels map into `attack_labels` during normalization).

---

## 1. Normalization Analysis

### 1NF Check

**Multi-valued fields (labels file):**
Each labeled record contains:
- `labels`: an **array** of tags (e.g., `["attacker_vpn", "foothold"]`)
- `rules`: a **nested dict** mapping label → list of matched signatures

These are 1NF violations (collections stored in a single field). In the planned normalized design, these unpack into separate rows in `attack_labels` linked to the parent event.

**Composite field (raw openvpn.log):**
The `message` column often embeds multiple attributes in one text blob. For example:
- `VERIFY OK: depth=1, C=AT, ST=Vienna, L=Vienna, O=Some Organisation GmbH, CN=OpenVPN CA, emailAddress=admin@organisation.cyberrange.at`
- `TLS: soft reset sec=3308/3308 bytes=45748/-1 pkts=649/0`

This is a 1NF violation if stored as one column. Resolution direction: retain raw message; optionally parse into atomic columns (depth, CN, cipher, bytes, etc.) during normalization/ETL for analytics.

**Repeating groups:** None (no phone1/phone2-style columns).

**1NF status: violated.**

### 2NF Check

Raw loading uses a single-column surrogate primary key (`vpn_event_id`). Partial dependencies only arise with composite keys. No composite key exists.

**2NF status: satisfied.**

### 3NF Check

**Transitive dependency (message type determines schema):**
The **message prefix** (e.g., `VERIFY OK`, `peer info`, `TLS`, `Control Channel`, `MULTI: Learn`) determines which sub-fields can be parsed from the rest of the line. For example:
- `VERIFY OK` lines contain depth, C, ST, L, O, CN, emailAddress
- `peer info` lines contain key=value (IV_VER, IV_PLAT, etc.)
- `TLS: soft reset` lines contain sec, bytes, pkts
- `TLS: Initial packet from` lines contain [AF_INET], sid

So `vpn_event_id` → message_type (derived from prefix) → populated field set. This is analogous to the audit log finding (`type` → field set).

**3NF status: violated.** Resolution direction: subtype tables or type-specific columns in the final 3NF schema; or retain a single `vpn_events` table with optional parsed columns and document the dependency in the normalization report.

### Preliminary Functional Dependencies

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `vpn_event_id` | all other attributes | Surrogate PK. |
| FD2 | `line_number` | all other attributes | Each log line is unique. Candidate key. |
| FD3 | message prefix / event type | populated field set | Message type determines which attributes can be parsed (3NF violation). |
| FD4 | `client` | constant per connection | Within a session, client (user/IP:port or IP:port) is fixed; meaningful for session grouping. |

---

## 2. Field-by-Field Summary (openvpn.log)

### Core fields (present in all records)

| Field | Present | Unique | Notes |
|---|---:|---:|---|
| `line_number` | 5537/5537 | 5537 | 1-based line number; candidate key |
| `event_timestamp` | 5537/5537 | ~many | Full timestamp with date and time (YYYY-MM-DD HH:MM:SS) |
| `client` | 5537/5537 | ~many | Client identifier: either `username/IP:port` (after auth) or `IP:port` (initial connection) |
| `message` | 5537/5537 | ~many | Free text; must be `TEXT` |

### Parsed sub-fields (analysis-only; not in raw DDL)

Following the same pattern as auth and audit notebooks: keep `df` with parsed columns for exploration; `df_raw` and DDL use only the raw blob.

| Field | Present | Notes |
|---|---:|---|
| `username` | ~many | Parsable from `client` when format is `user/IP:port`; NULL when client is `IP:port` only (pre-auth) |
| `client_ip` | 5537/5537 | Parsable from `client` (part after `/` or whole string if no slash) |
| `client_port` | 5537/5537 | Parsable from `client` (after final `:`) |
| `message_prefix` | 5537/5537 | First token or prefix of message (e.g. VERIFY OK, peer info, TLS) - drives event type |

Message content often contains key=value or key: value pairs; these can be parsed for analytics but are not stored as separate columns in the raw table.

### Multi-valued fields (labels file)

| Field | Present | Notes |
|---|---|---|
| `labels` (→ `vpn_event_category`) | 28/5537 | Array of attack-phase tags. All 28 labeled records have `["attacker_vpn", "foothold"]`. Stored as TEXT[] (PostgreSQL) or JSON (MySQL) in raw load. |
| `rules` (→ `vpn_signature_matches`) | 28/5537 | Nested dict mapping label → list of signature strings. Stored as JSONB (PostgreSQL) or JSON (MySQL). |

---

## 3. Event Type / Message Distribution

Message prefixes (first significant token or phrase) drive event semantics. Dominant patterns:

| Message prefix / type | Count | % | Notes |
|---|---:|---:|---|
| peer info | 2181 | 39.4% | Client capability flags (IV_VER, IV_PLAT, etc.) |
| VERIFY OK | 470 | 8.5% | Certificate verification (depth, C, ST, CN, …) |
| Outgoing Data Channel | 470 | 8.5% | Cipher/hash setup |
| Incoming Data Channel | 470 | 8.5% | Cipher/hash setup |
| TLS | 238 | 4.3% | Soft reset, Initial packet, etc. |
| Validating certificate... | 235 | 4.2% | EKU validation |
| VERIFY KU OK / VERIFY EKU OK | 470 | 8.5% | Key usage checks |
| Control Channel | 234 | 4.2% | TLS version, cipher, certificate info |
| MULTI / MULTI_sva / PUSH / SENT CONTROL | 264 | 4.8% | Session and routing |
| Peer Connection Initiated / Inactivity timeout | 131 | 2.4% | Connection lifecycle |
| TLS Error | 6 | 0.1% | Errors |

Most lines are TLS handshake and session-maintenance traffic. A single VPN connection produces dozens of lines (handshake, verify, data channel, control channel, peer info).

---

## 4. Attack Events (Ground Truth Labels)

28 labeled lines (4331–4358), all **Initial Access** (attacker VPN connection):

- **Lines 4331–4358:** Attacker connects from external IP **192.168.230.122** (port 53581) at 2022-01-24 03:01:00. The connection is authenticated as **jhall** (stolen/cracked credentials). Lines include:
  - TLS Initial packet from [AF_INET]192.168.230.122:53581
  - VERIFY OK (depth 0, CN=jhall)
  - Peer Connection Initiated with [AF_INET]192.168.230.122:53581
  - MULTI_sva / MULTI: Learn / MULTI: primary virtual IP (10.9.0.10)
  - Data Channel and Control Channel setup

- **Labels:** Every labeled record has `["attacker_vpn", "foothold"]`.
- **Rule:** `attacker.foothold.vpn.ip` - detection is based on attacker IP 192.168.230.122.

**Label distribution (28 labeled records):**
- `attacker_vpn`: 28
- `foothold`: 28

**Context (from data_scope_and_findings.md):** The attacker’s external IP is 192.168.230.122; after VPN login they receive internal IP 172.19.131.174. The compromised VPN user is jhall (192.168.230.165 is jhall’s legitimate client IP from another session). The 28 lines represent the attacker’s single VPN connection that establishes the foothold.

---

## 5. Key Findings for Schema Design

1. **Single attacker connection in labels:** All 28 labeled lines belong to one VPN session (192.168.230.122, 2022-01-24 03:01:00). Correlation with other logs (Apache, auth, audit) uses the VPN-assigned IP 172.19.131.174.

2. **Client identifier is composite:** The `client` field is either `username/IP:port` or `IP:port`. Raw table can store it as one VARCHAR/TEXT; normalization can split into `username`, `client_ip`, `client_port` (and optionally `client` for display).

3. **1NF violations in `labels` and `rules`:** Same pattern as Apache error and auth findings. Store as TEXT[]/JSONB (PostgreSQL) and JSON (MySQL) in raw load; normalize to `attack_labels` (and optionally signature tables).

4. **1NF violation in `message`:** Message often embeds multiple attributes (e.g. VERIFY OK key=value list). Keep as single TEXT in raw table; parsing into atomic columns is a normalization/ETL choice.

5. **3NF violation (message type → field set):** Message prefix determines which sub-fields exist. Normalization can introduce event_type or message_type and type-specific columns or subtype tables.

6. **Legitimate traffic dominates:** 5,509 unlabeled lines are mostly jhall/192.168.230.165, twhite/192.168.230.95, ahayes/192.168.231.127 (remote employees). The attacker (192.168.230.122) appears in 32 lines total; 28 of those are labeled.

---

## 6. DDL for Raw Loading (openvpn.log + labels)

This raw-load shape follows the project rule **Raw = truly raw**:
- Keep `message` as a single TEXT blob (1NF violation when it embeds multiple attributes).
- Keep `client` as a single string (username/IP:port or IP:port).
- Do **not** store message-parsed sub-fields (depth, CN, cipher, bytes, etc.) in the raw DDL.
- Multi-valued `labels` and nested `rules` from the label file are stored as-is (1NF violations; normalization unpacks them).

```sql
-- PostgreSQL
CREATE TABLE vpn_events_raw (
    vpn_event_id            SERIAL PRIMARY KEY,
    line_number             INTEGER NOT NULL,
    event_timestamp         TIMESTAMP WITH TIME ZONE,
    client                  VARCHAR(100) NOT NULL,
    message                 TEXT NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

```sql
-- MySQL
CREATE TABLE vpn_events_raw (
    vpn_event_id            INT AUTO_INCREMENT PRIMARY KEY,
    line_number             INT NOT NULL,
    event_timestamp         DATETIME,
    client                  VARCHAR(100) NOT NULL,
    message                 TEXT NOT NULL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Notes for Normalization Phase

1. **Unpack labels/rules to `attack_labels`:** Each (event, label) becomes one row; each (event, label, signature) becomes one row if signatures are modeled separately.

2. **Split `client` optionally:** For analytics, derive `username` (NULL when client is IP:port only), `client_ip`, `client_port` from `client`. Keep `client` for display or use as natural key component per session.

3. **Derive `event_type` or `message_type`:** From message prefix (VERIFY OK, peer info, TLS, Control Channel, MULTI, etc.) for consistent filtering and analytics.

4. **Parse message sub-fields only if needed:** VERIFY OK lines have depth, CN, etc.; TLS soft reset has sec, bytes, pkts. Parsing is optional and can live in views or ETL into normalized columns.

5. **Cross-log correlation:** The attacker’s VPN connection (192.168.230.122) is the entry point; the same actor appears in Apache, auth, and audit logs under the VPN-assigned IP 172.19.131.174. Join on IP and time for end-to-end attack chain analysis.
