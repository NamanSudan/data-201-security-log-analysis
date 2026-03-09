# Combined Normalization Plan — All Log and YAML Sources to 3NF

Based on: all 9 findings documents in `docs/data_exploration/notebook_findings/`,
`NormalizationRules.md` (Lecture 4/5, DATA 201, Spring 2026).

Scope: normalize every raw log and YAML source referenced in the findings to 3NF.
**Labels files are excluded** — the `labels` and `rules` annotation columns are out of scope.

---

## Table of Contents

1. [Source Inventory](#1-source-inventory)
2. [Shared Dimension Tables](#2-shared-dimension-tables)
3. [Per-Source Normalization](#3-per-source-normalization)
   - 3.1 [Hosts (servers.yaml)](#31-hosts-serversyaml)
   - 3.2 [Auth Log (intranet_server)](#32-auth-log-intranet_server)
   - 3.3 [DNS Log (inet-firewall)](#33-dns-log-inet-firewall)
   - 3.4 [VPN Log (vpn)](#34-vpn-log-vpn)
   - 3.5 [Audit Log — intranet_server](#35-audit-log--intranet_server)
   - 3.6 [Audit Log — internal_share](#36-audit-log--internal_share)
   - 3.7 [Apache Access Log (intranet_server)](#37-apache-access-log-intranet_server)
   - 3.8 [Apache Error Log (intranet_server)](#38-apache-error-log-intranet_server)
   - 3.9 [CPU Metrics (internal_share)](#39-cpu-metrics-internal_share)
4. [Cross-Source Integration](#4-cross-source-integration)
5. [Complete 3NF Table Inventory](#5-complete-3nf-table-inventory)
6. [Functional Dependency Registry](#6-functional-dependency-registry)

---

## 1. Source Inventory

| # | Findings doc | Raw source file(s) | Rows | Raw table name |
|---|---|---|---:|---|
| 1 | `naman_hosts_findings.md` | `processing/config/servers.yaml` | 22 hosts / 66 log configs | `hosts_raw`, `host_log_configs_raw` |
| 2 | `hunt_auth_logs_findings.md` | `gather/intranet_server/logs/auth.log` | 272 | `auth_events_raw` |
| 3 | `hunt_dns_logs_findings.md` | `gather/inet-firewall/logs/dnsmasq.log` | 275,900 | `dns_events_raw` |
| 4 | `hunt_vpn_logs_findings.md` | `gather/vpn/logs/openvpn.log` | 5,537 | `vpn_events_raw` |
| 5 | `naman_audit_intranet_findings.md` | `gather/intranet_server/logs/audit/audit.log` | 2,316 | `audit_events_intranet_raw` |
| 6 | `naman_audit_internal_share_findings.md` | `gather/internal_share/logs/audit/audit.log` | 732 | `audit_events_internal_share_raw` |
| 7 | `ishaan_apache_access_findings.md` | `gather/intranet_server/logs/apache2/...-access_log.2` | varies | `http_access_events` |
| 8 | `ishaan_apache_error_findings.md` | `gather/intranet_server/logs/apache2/...-error_log.2` | 35 | `http_events` |
| 9 | `ishaan_cpu_internal_share_findings.md` | `gather/internal_share/logs/2022-01-21-system_cpu.log` | 1,919 | `system_cpu_events` |

**Total raw rows across all sources: ~286,733**

---

## 2. Shared Dimension Tables

These tables are referenced by multiple fact/event tables and must be created first.

### 2.1 `hosts` (from servers.yaml)

The hosts dimension is the backbone: every event table acquires a `host_id` FK linking back to this table. Hosts normalization is detailed in §3.1.

### 2.2 `distributions` (extracted from hosts for 3NF)

Resolves the transitive dependency `distribution_release → (distribution, distribution_version)`.

```sql
CREATE TABLE distributions (
    distribution_release  VARCHAR(20) PRIMARY KEY,
    distribution          VARCHAR(50) NOT NULL,
    distribution_version  VARCHAR(20) NOT NULL
);
```

| distribution_release | distribution | distribution_version |
|---|---|---|
| bionic | Ubuntu | 18.04 |
| stretch | Debian | 9.11 |

---

## 3. Per-Source Normalization

### 3.1 Hosts (servers.yaml)

**Findings doc:** `naman_hosts_findings.md`
**Raw tables:** `hosts_raw` (15 cols, 22 rows), `host_log_configs_raw` (7 cols, 66 rows)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | **VIOLATED** | `groups` stores list of 2–5 values | Junction table `host_groups` |
| 1NF | **VIOLATED** | `fqdns` stores list of 0–4 values | Separate table `host_fqdns` |
| 1NF | **VIOLATED** | `ipv4_addresses` stores list of 1–3 values | Separate table `host_ipv4_addresses` |
| 1NF | **VIOLATED** | `ipv6_addresses` stores list of 1–3 values | Separate table `host_ipv6_addresses` |
| 1NF | **VIOLATED** | `logs` is list of dicts | Already separated as `host_log_configs_raw` |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `distribution_release → (distribution, distribution_version)` | Extract `distributions` lookup table |

#### Target 3NF Tables

**`hosts`** — core dimension table (22 rows)

```sql
CREATE TABLE hosts (
    host_id                 SERIAL PRIMARY KEY,
    host_key                VARCHAR(50) NOT NULL UNIQUE,
    hostname                VARCHAR(100) NOT NULL UNIQUE,
    username                VARCHAR(50),
    openvpn_user            VARCHAR(50),
    distribution_release    VARCHAR(20) NOT NULL REFERENCES distributions(distribution_release),
    default_ipv4_address    VARCHAR(45) NOT NULL,
    default_ipv6_address    VARCHAR(45) NOT NULL,
    timezone                VARCHAR(10) NOT NULL
);
```

Columns removed vs. raw: `groups`, `fqdns`, `ipv4_addresses`, `ipv6_addresses` (→ junction tables), `distribution`, `distribution_version` (→ `distributions` lookup).

**`host_groups`** — resolves multivalued `groups` (1NF)

```sql
CREATE TABLE host_groups (
    host_id     INT NOT NULL REFERENCES hosts(host_id),
    group_name  VARCHAR(50) NOT NULL,
    PRIMARY KEY (host_id, group_name)
);
```

**`host_fqdns`** — resolves multivalued `fqdns` (1NF)

```sql
CREATE TABLE host_fqdns (
    host_id  INT NOT NULL REFERENCES hosts(host_id),
    fqdn     VARCHAR(255) NOT NULL,
    PRIMARY KEY (host_id, fqdn)
);
```

**`host_ipv4_addresses`** — resolves multivalued `ipv4_addresses` (1NF)

```sql
CREATE TABLE host_ipv4_addresses (
    host_id       INT NOT NULL REFERENCES hosts(host_id),
    ipv4_address  VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv4_address)
);
```

**`host_ipv6_addresses`** — resolves multivalued `ipv6_addresses` (1NF)

```sql
CREATE TABLE host_ipv6_addresses (
    host_id       INT NOT NULL REFERENCES hosts(host_id),
    ipv6_address  VARCHAR(45) NOT NULL,
    PRIMARY KEY (host_id, ipv6_address)
);
```

**`host_log_configs`** — already decomposed from `logs` (1NF resolved by raw load)

```sql
CREATE TABLE host_log_configs (
    config_id       SERIAL PRIMARY KEY,
    host_id         INT NOT NULL REFERENCES hosts(host_id),
    log_path        TEXT NOT NULL,
    log_type        VARCHAR(50) NOT NULL,
    codec           VARCHAR(20),
    file_chunk_size INT,
    add_field_json  TEXT
);
```

#### 3NF Verification

- All values atomic (1NF).
- No composite PKs with non-key partial dependencies (2NF).
- `distribution_release` is now an FK into `distributions`; no transitive deps remain (3NF).

---

### 3.2 Auth Log (intranet_server)

**Findings doc:** `hunt_auth_logs_findings.md`
**Raw source:** `gather/intranet_server/logs/auth.log` (272 lines)
**Raw table:** `auth_events_raw` (7 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | **VIOLATED** | `message` embeds key-value sub-fields (TTY, PWD, USER, COMMAND for sudo; username/IP/port for sshd; user/uid for CRON) | Parse into atomic columns |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `process_name → populated field set` (e.g., sshd lines have remote_ip; sudo lines have command; CRON lines have uid) | Add explicit `event_type` discriminator; nullable type-specific columns |

#### Target 3NF Table

**`auth_events`**

```sql
CREATE TABLE auth_events (
    auth_event_id    SERIAL PRIMARY KEY,
    host_id          INT NOT NULL REFERENCES hosts(host_id),
    line_number      INT NOT NULL,
    event_timestamp  TIMESTAMP WITH TIME ZONE,
    hostname         VARCHAR(100),
    process_name     VARCHAR(50) NOT NULL,
    pid              INT,
    event_type       VARCHAR(30) NOT NULL,
    username         VARCHAR(50),
    uid              INT,
    remote_ip        VARCHAR(45),
    remote_port      INT,
    auth_method      VARCHAR(30),
    terminal         VARCHAR(50),
    pwd              TEXT,
    target_user      VARCHAR(50),
    command          TEXT,
    session_id       VARCHAR(30),
    message          TEXT NOT NULL
);
```

**Key design decisions:**

- `event_type` (derived from `process_name` + message pattern: `cron_session_open`, `cron_session_close`, `ssh_accepted`, `ssh_disconnect`, `sudo_command`, `su_switch`, `session_new`, `session_removed`, etc.) becomes an explicit column. Type-specific parsed fields (`remote_ip`, `command`, etc.) are nullable and directly dependent on the PK, resolving the 3NF transitive dependency.
- `message` (raw TEXT) is retained for audit/display alongside the parsed atomic columns.
- `host_id` FK enables future union with auth logs from other hosts.
- `username` and `target_user` are separate columns to handle multi-principal events (e.g., `su` from www-data to jhall).

#### Parsed fields by event_type

| event_type | username | uid | remote_ip | remote_port | auth_method | terminal | pwd | target_user | command | session_id |
|---|---|---|---|---|---|---|---|---|---|---|
| `cron_session_open` | Y | sometimes | — | — | — | — | — | — | — | — |
| `cron_session_close` | Y | sometimes | — | — | — | — | — | — | — | — |
| `ssh_accepted` | Y | — | Y | Y | Y | — | — | — | — | — |
| `ssh_disconnect` | Y | — | Y | Y | — | — | — | — | — | — |
| `sudo_command` | Y | — | — | — | — | Y | Y | Y | Y | — |
| `su_switch` | Y | — | — | — | — | Y | — | Y | — | — |
| `session_new` | Y | — | — | — | — | — | — | — | — | Y |
| `session_removed` | Y | — | — | — | — | — | — | — | — | Y |

---

### 3.3 DNS Log (inet-firewall)

**Findings doc:** `hunt_dns_logs_findings.md`
**Raw source:** `gather/inet-firewall/logs/dnsmasq.log` (275,900 lines)
**Raw table:** `dns_events_raw` (6 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | **VIOLATED** | `message` embeds event_action, query_type, domain, client_ip, upstream_ip, reply_value in a single text blob | Parse into atomic columns |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `event_action → populated field set` (query has client_ip; forwarded has upstream_ip; reply/cached have reply_value) | Add explicit `event_action` column; nullable type-specific columns |

#### Target 3NF Table

**`dns_events`**

```sql
CREATE TABLE dns_events (
    dns_event_id     SERIAL PRIMARY KEY,
    host_id          INT NOT NULL REFERENCES hosts(host_id),
    line_number      INT NOT NULL,
    event_timestamp  TIMESTAMP WITH TIME ZONE,
    host             VARCHAR(50),
    process          VARCHAR(100),
    event_action     VARCHAR(20) NOT NULL,
    query_type       VARCHAR(10),
    domain           TEXT,
    client_ip        VARCHAR(45),
    upstream_ip      VARCHAR(45),
    reply_value      TEXT,
    message          TEXT NOT NULL
);
```

**Key design decisions:**

- `event_action` (one of: `query`, `forwarded`, `reply`, `cached`, `nameserver`, `failed`) is extracted as an explicit column. This resolves the 3NF transitive dependency: type-specific fields (`query_type`, `client_ip`, `upstream_ip`, `reply_value`) are nullable and directly dependent on the PK.
- `message` is retained for audit/display.
- Syslog timestamp year must be inferred from scenario context (2022) at ETL time.

#### Parsed fields by event_action

| event_action | query_type | domain | client_ip | upstream_ip | reply_value |
|---|---|---|---|---|---|
| `query` | Y (A/TXT/AAAA) | Y | Y | — | — |
| `forwarded` | — | Y | — | Y | — |
| `reply` | — | Y | — | — | Y |
| `cached` | — | Y | — | — | Y |
| `nameserver` | — | — | — | — | — |
| `failed` | — | — | — | — | — |

---

### 3.4 VPN Log (vpn)

**Findings doc:** `hunt_vpn_logs_findings.md`
**Raw source:** `gather/vpn/logs/openvpn.log` (5,537 lines)
**Raw table:** `vpn_events_raw` (5 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | **VIOLATED** | `client` is composite (`username/IP:port` or `IP:port`) | Split into `username`, `client_ip`, `client_port` |
| 1NF | **VIOLATED** | `message` embeds depth, CN, cipher, sec/bytes/pkts, etc. | Parse selectively into atomic columns |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `message_type → populated field set` (VERIFY OK has depth/CN; TLS soft reset has sec/bytes/pkts) | Add explicit `message_type` column; nullable type-specific columns |

#### Target 3NF Table

**`vpn_events`**

```sql
CREATE TABLE vpn_events (
    vpn_event_id     SERIAL PRIMARY KEY,
    host_id          INT NOT NULL REFERENCES hosts(host_id),
    line_number      INT NOT NULL,
    event_timestamp  TIMESTAMP WITH TIME ZONE,
    username         VARCHAR(50),
    client_ip        VARCHAR(45) NOT NULL,
    client_port      INT NOT NULL,
    message_type     VARCHAR(50) NOT NULL,
    depth            INT,
    cn               VARCHAR(100),
    cipher           VARCHAR(100),
    tls_sec          INT,
    tls_bytes        INT,
    tls_pkts         INT,
    message          TEXT NOT NULL
);
```

**Key design decisions:**

- `client` is decomposed: `username` (NULL when client is `IP:port` pre-auth), `client_ip`, `client_port`.
- `message_type` (derived from message prefix: `verify_ok`, `peer_info`, `tls_initial`, `tls_soft_reset`, `data_channel`, `control_channel`, `multi_learn`, `connection_initiated`, etc.) resolves the 3NF dependency.
- Only high-value parsed fields are promoted to columns (`depth`, `cn`, `cipher`, `tls_sec`, `tls_bytes`, `tls_pkts`). Remaining message content stays in `message`.

#### Parsed fields by message_type

| message_type | depth | cn | cipher | tls_sec | tls_bytes | tls_pkts |
|---|---|---|---|---|---|---|
| `verify_ok` | Y | Y | — | — | — | — |
| `tls_soft_reset` | — | — | — | Y | Y | Y |
| `data_channel` | — | — | Y | — | — | — |
| `control_channel` | — | — | Y | — | — | — |
| `peer_info` | — | — | — | — | — | — |
| `connection_initiated` | — | — | — | — | — | — |
| others | — | — | — | — | — | — |

---

### 3.5 Audit Log — intranet_server

**Findings doc:** `naman_audit_intranet_findings.md`
**Raw source:** `gather/intranet_server/logs/audit/audit.log` (2,316 lines)
**Raw table:** `audit_events_intranet_raw` (40 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | **VIOLATED** | `msg` column packs multiple key-value pairs (op, acct, exe, hostname, addr, terminal, res, unit, comm, id, cwd, cmd) into one TEXT blob | Unpack into atomic columns |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `type → populated field set` (15 event types each use a different column subset) | Two options below |

#### 3NF Resolution Strategy

**Recommended approach (pragmatic single-table with unpacked `msg`):**

Keep one `audit_events` table with the `msg` blob unpacked into atomic columns. The `type` column serves as a discriminator; type-specific columns are nullable. This avoids an explosion of subtype tables while still achieving atomic values.

This approach satisfies 1NF (all values atomic after unpacking) and resolves the 3NF transitive dependency by making each parsed field functionally dependent on the PK through the combination of `type` and the PK. The nullable columns for inapplicable event types do not cause update anomalies.

**Strict 3NF alternative (subtype tables):**

If the instructor requires formal decomposition, use a parent table (`audit_events`) with shared columns and child tables for each event category:

- `audit_pam_events` — USER_ACCT, CRED_ACQ, USER_START, CRED_DISP, USER_END, USER_AUTH, CRED_REFR
- `audit_login_events` — LOGIN, USER_LOGIN
- `audit_service_events` — SERVICE_START, SERVICE_STOP
- `audit_cmd_events` — USER_CMD
- `audit_kernel_events` — AVC, SYSCALL, PROCTITLE

Each child table FK-references the parent via `event_id`. This document proceeds with the **recommended pragmatic approach**.

#### Target 3NF Table

**`audit_events`** — merges intranet_server (2,316 rows) and internal_share (732 rows) with `host_id` discriminator.

```sql
CREATE TABLE audit_events (
    event_id         SERIAL PRIMARY KEY,
    host_id          INT NOT NULL REFERENCES hosts(host_id),
    line_number      INT NOT NULL,
    type             VARCHAR(20) NOT NULL,
    epoch            DOUBLE PRECISION NOT NULL,
    serial           INT NOT NULL,
    event_timestamp  TIMESTAMP WITH TIME ZONE NOT NULL,
    pid              INT,
    uid              INT,
    auid             BIGINT,
    ses              BIGINT,

    -- Unpacked from msg (PAM events)
    msg_op           VARCHAR(30),
    msg_acct         VARCHAR(50),
    msg_exe          TEXT,
    msg_hostname     VARCHAR(50),
    msg_addr         VARCHAR(45),
    msg_terminal     VARCHAR(30),
    msg_res          VARCHAR(20),

    -- Unpacked from msg (SERVICE events)
    msg_unit         VARCHAR(100),
    msg_comm         VARCHAR(50),

    -- Unpacked from msg (USER_LOGIN)
    msg_id           INT,

    -- Unpacked from msg (USER_CMD)
    msg_cwd          TEXT,
    msg_cmd          TEXT,

    -- Top-level fields (LOGIN)
    old_auid         BIGINT,
    old_ses          BIGINT,
    tty              VARCHAR(30),
    res              VARCHAR(10),

    -- Top-level fields (AVC)
    apparmor         VARCHAR(20),
    operation        VARCHAR(30),
    info             TEXT,
    profile          VARCHAR(50),
    name             TEXT,

    -- Top-level fields (SYSCALL)
    arch             VARCHAR(20),
    syscall_num      INT,
    success          VARCHAR(5),
    exit_code        BIGINT,
    a0               VARCHAR(20),
    a1               VARCHAR(20),
    a2               VARCHAR(20),
    a3               VARCHAR(20),
    items            INT,
    ppid             INT,
    gid              INT,
    euid             INT,
    suid             INT,
    fsuid            INT,
    egid             INT,
    sgid             INT,
    fsgid            INT,
    exe              TEXT,
    key_field        VARCHAR(20),

    -- Top-level fields (PROCTITLE)
    proctitle        TEXT,

    -- Retained raw blob for audit
    msg              TEXT
);
```

**Key design decisions:**

- `msg` is unpacked into `msg_op`, `msg_acct`, `msg_exe`, `msg_hostname`, `msg_addr`, `msg_terminal`, `msg_res`, `msg_unit`, `msg_comm`, `msg_id`, `msg_cwd`, `msg_cmd`. Each is nullable and populated only for applicable event types.
- The original `msg` TEXT is retained for traceability.
- `host_id` FK enables merge of intranet_server and internal_share audit logs into one table.
- `auid` and `ses` use `BIGINT` to accommodate the unset sentinel value `4294967295`.
- Renamed: `syscall` → `syscall_num`, `exit` → `exit_code`, `key` → `key_field` to avoid SQL reserved word conflicts.

---

### 3.6 Audit Log — internal_share

**Findings doc:** `naman_audit_internal_share_findings.md`
**Raw source:** `gather/internal_share/logs/audit/audit.log` (732 lines)
**Raw table:** `audit_events_internal_share_raw` (40 cols)

#### Normalization

**Merged into `audit_events` (§3.5).** Same schema, same violations, same resolution. The two audit log files share identical auditd format and the same 40-column structure. Differences:

| Attribute | intranet_server | internal_share |
|---|---|---|
| Rows | 2,316 | 732 |
| Event types | 15 | 11 (missing USER_LOGIN, USER_AUTH, USER_CMD, CRED_REFR) |
| Attack events | 9 (privilege escalation) | 2 (exfiltration service) |
| Network context | 21 rows with real IP 172.19.131.174 | None (all hostname=?, addr=?) |

Both load into `audit_events` with `host_id` distinguishing the source host. Combined: **3,048 rows**.

---

### 3.7 Apache Access Log (intranet_server)

**Findings doc:** `ishaan_apache_access_findings.md`
**Raw source:** `gather/intranet_server/logs/apache2/...-access_log.2`
**Raw table:** `http_access_events` (15 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | Satisfied | URL is already split into `url_path` and `query_string`; all other fields are atomic | — |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `request_url → (url_path, query_string)` — URL components are derived from the full URL | Drop `request_url` or treat `url_path`/`query_string` as the canonical form |
| 3NF | **VIOLATED** | `query_string → decoded_command` — webshell command is fully determined by the query string | Drop `decoded_command` (compute via view) or document as denormalized |

#### Target 3NF Table

**`http_access_events`**

```sql
CREATE TABLE http_access_events (
    http_access_event_id  SERIAL PRIMARY KEY,
    host_id               INT NOT NULL REFERENCES hosts(host_id),
    event_id              INT NOT NULL,
    event_timestamp       TIMESTAMP WITH TIME ZONE,
    client_ip             VARCHAR(45),
    http_method           VARCHAR(10),
    url_path              TEXT,
    query_string          TEXT,
    status_code           SMALLINT,
    bytes_sent            INT,
    request_type          VARCHAR(20)
);
```

**Key design decisions:**

- `request_url` is dropped. `url_path` and `query_string` are the atomic canonical form. The full URL is reconstructable from `url_path || '?' || query_string`.
- `decoded_command` is dropped from the base table. It is a derived column (`base64_decode(query_string.wp_meta)`) and can be computed via a view or generated column:

```sql
CREATE VIEW http_access_events_with_commands AS
SELECT *,
       decode_wp_meta(query_string) AS decoded_command
FROM http_access_events;
```

- `host_id` FK enables future multi-host HTTP log integration.

---

### 3.8 Apache Error Log (intranet_server)

**Findings doc:** `ishaan_apache_error_findings.md`
**Raw source:** `gather/intranet_server/logs/apache2/...-error_log.2` (35 lines)
**Raw table:** `http_events` (9 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | Satisfied | (labels/rules excluded from scope) | — |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **VIOLATED** | `log_level → (module, severity)` — composite field encodes two attributes | Split into `module` and `severity` columns |

#### Target 3NF Table

**`http_error_events`**

```sql
CREATE TABLE http_error_events (
    http_error_event_id  SERIAL PRIMARY KEY,
    host_id              INT NOT NULL REFERENCES hosts(host_id),
    event_id             INT NOT NULL,
    event_timestamp      TIMESTAMP WITH TIME ZONE,
    module               VARCHAR(50),
    severity             VARCHAR(20),
    client_ip            VARCHAR(45),
    message              TEXT
);
```

**Key design decisions:**

- `log_level` (e.g., `authz_core:error`) is split into `module` (`authz_core`) and `severity` (`error`).
- `client_ip` retained even though all 35 records share one IP — the column becomes meaningful when multiple hosts/logs are combined.
- `host_id` FK enables multi-host integration.

---

### 3.9 CPU Metrics (internal_share)

**Findings doc:** `ishaan_cpu_internal_share_findings.md`
**Raw source:** `gather/internal_share/logs/2022-01-21-system_cpu.log` (1,919 records)
**Raw table:** `system_cpu_events` (12 cols)

#### Violations

| NF | Status | Violation | Resolution |
|---|---|---|---|
| 1NF | Satisfied | All fields are scalar after `json_normalize` | — |
| 2NF | Satisfied | Single-column PK | — |
| 3NF | **Acceptable** | `hostname → cpu_cores` (trivial with 1 host; deferred) | Move `cpu_cores` to `hosts` when multiple hosts present |
| 3NF | **Acceptable** | `cpu_total_pct ≈ sum(component pcts)` (derived column) | Drop or keep with documentation |

#### Target 3NF Table

**`system_cpu_events`**

```sql
CREATE TABLE system_cpu_events (
    system_cpu_event_id  SERIAL PRIMARY KEY,
    host_id              INT NOT NULL REFERENCES hosts(host_id),
    event_timestamp      TIMESTAMP WITH TIME ZONE NOT NULL,
    cpu_user_pct         NUMERIC(6,4),
    cpu_system_pct       NUMERIC(6,4),
    cpu_idle_pct         NUMERIC(6,4),
    cpu_iowait_pct       NUMERIC(6,4),
    cpu_steal_pct        NUMERIC(6,4),
    cpu_softirq_pct      NUMERIC(6,4)
);
```

**Key design decisions:**

- `hostname` is replaced by `host_id` FK into `hosts`, resolving `hostname → cpu_cores` (cores can be stored in the hosts table if needed).
- `cpu_total_pct` is dropped — it is the sum of component percentages and can be computed via a view:

```sql
CREATE VIEW system_cpu_events_with_total AS
SELECT *,
       cpu_user_pct + cpu_system_pct + cpu_iowait_pct
       + cpu_steal_pct + cpu_softirq_pct AS cpu_total_pct
FROM system_cpu_events;
```

- `metricset_period_ms` (constant 45000) and `cpu_cores` (constant 2) are dropped from the table. `cpu_cores` can move to the `hosts` table as an optional attribute; `metricset_period_ms` is metadata that can be documented or stored in a config table.

---

## 4. Cross-Source Integration

### 4.1 Host dimension linkage

Every event table carries a `host_id` FK into `hosts`. This enables:

- Joining any event type to host metadata (IP, groups, FQDN, OS).
- Filtering events by host group (`servers`, `dmz`, `employees`, etc.) via the `host_groups` junction table.
- Correlation across log sources for the same host (e.g., auth + audit on `intranet-server`).

### 4.2 Audit log merge

`audit_events` merges intranet_server (2,316 rows) and internal_share (732 rows). The `host_id` column discriminates source host. Both files share the same auditd format and column schema.

### 4.3 Cross-log attack correlation

The attacker's activity spans multiple log sources:

| Attack phase | Log source | Key fields for join |
|---|---|---|
| Initial access (VPN) | `vpn_events` | `client_ip = 192.168.230.122`, assigned IP `172.19.131.174` |
| Reconnaissance (HTTP) | `http_access_events`, `http_error_events` | `client_ip = 172.19.131.174` |
| Privilege escalation (auth) | `auth_events` | `username = jhall`, `remote_ip = 172.19.131.174` |
| Privilege escalation (audit) | `audit_events` | `msg_hostname/msg_addr = 172.19.131.174`, `uid = 33/1002` |
| Exfiltration (DNS) | `dns_events` | `client_ip = 10.143.0.103`, domain pattern `*.kennedy-mendoza.info` |
| Exfiltration (audit) | `audit_events` (internal_share) | `msg_unit = put` |
| Resource impact | `system_cpu_events` | `event_timestamp` overlap with exfiltration window |

Cross-source joins use `event_timestamp` windows and IP-based keys. The `hosts` table provides the mapping from hostname to IP address.

### 4.4 Timestamp handling

| Source | Timestamp format | Year present | Resolution |
|---|---|---|---|
| auth.log | `Mon DD HH:MM:SS` | No | Infer year (2022) from scenario context at ETL |
| dnsmasq.log | `Mon DD HH:MM:SS` | No | Infer year (2022) at ETL |
| openvpn.log | `YYYY-MM-DD HH:MM:SS` | Yes | Direct parse |
| audit.log | Unix epoch (ms precision) | Yes | Convert `epoch → TIMESTAMP WITH TIME ZONE` |
| access_log | `DD/Mon/YYYY:HH:MM:SS ±ZZZZ` | Yes | Direct parse with timezone |
| error_log | Full timestamp (µs precision) | Yes | Direct parse |
| system_cpu | ISO 8601 (UTC) | Yes | Direct parse |

All target tables use `TIMESTAMP WITH TIME ZONE` for consistent cross-source querying.

---

## 5. Complete 3NF Table Inventory

### Dimension Tables

| Table | PK | Rows | Source |
|---|---|---:|---|
| `distributions` | `distribution_release` | 2 | servers.yaml (extracted) |
| `hosts` | `host_id` | 22 | servers.yaml |
| `host_groups` | `(host_id, group_name)` | ~66 | servers.yaml (exploded) |
| `host_fqdns` | `(host_id, fqdn)` | ~20 | servers.yaml (exploded) |
| `host_ipv4_addresses` | `(host_id, ipv4_address)` | ~24 | servers.yaml (exploded) |
| `host_ipv6_addresses` | `(host_id, ipv6_address)` | ~24 | servers.yaml (exploded) |
| `host_log_configs` | `config_id` | 66 | servers.yaml |

### Event/Fact Tables

| Table | PK | Rows | Source(s) |
|---|---|---:|---|
| `auth_events` | `auth_event_id` | 272 | auth.log (intranet_server) |
| `dns_events` | `dns_event_id` | 275,900 | dnsmasq.log (inet-firewall) |
| `vpn_events` | `vpn_event_id` | 5,537 | openvpn.log (vpn) |
| `audit_events` | `event_id` | 3,048 | audit.log (intranet_server + internal_share) |
| `http_access_events` | `http_access_event_id` | varies | access_log (intranet_server) |
| `http_error_events` | `http_error_event_id` | 35 | error_log (intranet_server) |
| `system_cpu_events` | `system_cpu_event_id` | 1,919 | system_cpu.log (internal_share) |

**Total: 14 tables** (7 dimension/junction + 7 event/fact).

---

## 6. Functional Dependency Registry

All FDs across normalized tables. Only non-trivial FDs are listed.

### Hosts domain

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `hosts` | FD-H1 | `host_id → host_key, hostname, username, openvpn_user, distribution_release, default_ipv4_address, default_ipv6_address, timezone` |
| `hosts` | FD-H2 | `host_key → all` (candidate key) |
| `hosts` | FD-H3 | `hostname → all` (candidate key) |
| `hosts` | FD-H4 | `openvpn_user → username` (when both present, they always match) |
| `distributions` | FD-D1 | `distribution_release → distribution, distribution_version` |

### Auth events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `auth_events` | FD-A1 | `auth_event_id → all` (PK) |
| `auth_events` | FD-A2 | `(host_id, line_number) → all` (candidate key within a host) |
| `auth_events` | FD-A3 | `process_name → event_type family` (used for parsing, not a storage dependency in 3NF) |

### DNS events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `dns_events` | FD-N1 | `dns_event_id → all` (PK) |
| `dns_events` | FD-N2 | `(host_id, line_number) → all` (candidate key within a host) |

### VPN events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `vpn_events` | FD-V1 | `vpn_event_id → all` (PK) |
| `vpn_events` | FD-V2 | `(host_id, line_number) → all` (candidate key within a host) |

### Audit events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `audit_events` | FD-U1 | `event_id → all` (PK) |
| `audit_events` | FD-U2 | `(host_id, line_number) → all` (candidate key within a host) |
| `audit_events` | FD-U3 | `serial → epoch, event_timestamp` (multi-line events share timestamp) |

### HTTP access events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `http_access_events` | FD-HA1 | `http_access_event_id → all` (PK) |
| `http_access_events` | FD-HA2 | `(host_id, event_id) → all` (candidate key within a host) |

### HTTP error events

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `http_error_events` | FD-HE1 | `http_error_event_id → all` (PK) |
| `http_error_events` | FD-HE2 | `(host_id, event_id) → all` (candidate key within a host) |

### CPU metrics

| Table | FD | Determinant → Dependent(s) |
|---|---|---|
| `system_cpu_events` | FD-C1 | `system_cpu_event_id → all` (PK) |
| `system_cpu_events` | FD-C2 | `(host_id, event_timestamp) → all` (candidate natural key) |
