# Hosts Table Findings - servers.yaml

Source: `processing/config/servers.yaml` (22 hosts, YAML dictionary).
Analysis notebook: `notebooks/01_explore_hosts.ipynb`.
Staging tables: `stg_host_raw` (15 columns, 22 rows), `stg_host_log_config_raw` (7 columns, 66 rows).

---

## 1. 1NF Violations

Five fields in `stg_host_raw` violate first normal form by storing multiple values in a single column.

| Field | Violation | Values per host | Resolution direction |
|---|---|---|---|
| `groups` | Multi-valued list (2-5 values, 17 distinct groups) | 2-5 | Junction table: `host_groups(host_id, group_name)` |
| `fqdns` | Multi-valued list (0-4 values) | 0-4 | Separate table: `host_fqdns(host_id, fqdn)` |
| `ipv4_addresses` | Multi-valued list (only inet-firewall has >1) | 1-3 | Separate table or keep default only (21/22 hosts have 1) |
| `ipv6_addresses` | Multi-valued list (only inet-firewall has >1) | 1-3 | Separate table or keep default only (21/22 hosts have 1) |
| `logs` | Multi-valued AND composite (list of dicts) | 1-9 | Already separated as `stg_host_log_config_raw` |

2NF violations cannot exist in these raw tables because both use single-column surrogate primary keys (`host_id`, `config_id`). Partial dependencies only arise with composite keys. 2NF becomes relevant when multi-valued fields are decomposed into junction tables during normalization.

3NF analysis is deferred to `docs/schema_normalization.md`. The observed correlation `distribution_release -> distribution, distribution_version` (see FD5 below) is the primary candidate to validate in final design.

---

## 2. Preliminary Functional Dependencies

These FDs are identified from the data and the business rules of the testbed. They feed into the FD identification phase in `docs/schema_normalization.md`.

| FD | Determinant | Dependent(s) | Reasoning |
|---|---|---|---|
| FD1 | `host_key` | all other attributes | Each YAML key uniquely identifies one host. Candidate key. |
| FD2 | `hostname` | all other attributes | Each hostname is unique across the testbed. Candidate key. |
| FD3 | `default_ipv4_address` | `hostname` | Observed in this dataset (each host has a unique default IPv4; needs validation across datasets, not yet confirmed as a true FD). |
| FD4 | `openvpn_user` | `username` | Observed in this dataset (always the same value when both present, but only 3 hosts). |
| FD5 | `distribution_release` | `distribution`, `distribution_version` | `bionic` always means Ubuntu 18.04; `stretch` always means Debian 9.11. Observed in this dataset and a candidate transitive dependency to validate in final design. |

---

## 3. DDL for Raw Loading

Column mapping tables with both PostgreSQL and MySQL types are in the notebook (section 6). The DDL below is for 1:1 raw data loading before any normalization.

### stg_host_raw

```sql
-- PostgreSQL
CREATE TABLE stg_host_raw (
    host_id SERIAL PRIMARY KEY,
    host_key VARCHAR(50) NOT NULL UNIQUE,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    groups TEXT NOT NULL,
    username VARCHAR(50),
    openvpn_user VARCHAR(50),
    distribution VARCHAR(50) NOT NULL,
    distribution_release VARCHAR(20) NOT NULL,
    distribution_version VARCHAR(20) NOT NULL,
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    ipv4_addresses TEXT NOT NULL,
    ipv6_addresses TEXT NOT NULL,
    fqdns TEXT,
    timezone VARCHAR(10) NOT NULL
);
```

```sql
-- MySQL
CREATE TABLE stg_host_raw (
    host_id INT AUTO_INCREMENT PRIMARY KEY,
    host_key VARCHAR(50) NOT NULL UNIQUE,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    groups TEXT NOT NULL,
    username VARCHAR(50),
    openvpn_user VARCHAR(50),
    distribution VARCHAR(50) NOT NULL,
    distribution_release VARCHAR(20) NOT NULL,
    distribution_version VARCHAR(20) NOT NULL,
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    ipv4_addresses TEXT NOT NULL,
    ipv6_addresses TEXT NOT NULL,
    fqdns TEXT,
    timezone VARCHAR(10) NOT NULL
);
```

### stg_host_log_config_raw

The `logs` nested composite field (array of dicts, 5 keys, 11 log types) maps to this separate table. `add_field` is serialized as a JSON string.

```sql
-- PostgreSQL
CREATE TABLE stg_host_log_config_raw (
    config_id SERIAL PRIMARY KEY,
    host_id INT NOT NULL REFERENCES stg_host_raw(host_id),
    log_path TEXT NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    codec VARCHAR(20),
    file_chunk_size INT,
    add_field_json TEXT
);
```

```sql
-- MySQL
CREATE TABLE stg_host_log_config_raw (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT NOT NULL,
    log_path TEXT NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    codec VARCHAR(20),
    file_chunk_size INT,
    add_field_json TEXT,
    FOREIGN KEY (host_id) REFERENCES stg_host_raw(host_id)
);
```

---

## 4. Notes for Normalization Phase

To be addressed in `docs/schema_normalization.md`:

1. **Multi-valued field decomposition**: The 5 fields in section 1 need separate tables to satisfy 1NF. For `ipv4_addresses` and `ipv6_addresses`, the team should decide whether to create separate tables or keep only the default columns, since 21/22 hosts have exactly one address.

2. **Transitive dependency (FD5)**: `distribution_release` determines `distribution` and `distribution_version`. For 3NF, consider a `distributions` lookup table. With only 2 distinct combinations across 22 hosts, weigh whether the decomposition is worth the complexity.

3. **add_field_json**: The `stg_host_log_config_raw` table stores `add_field` as a JSON string with 4 distinct metadata keys (documented in notebook section 2.5). Decide whether this needs its own table (e.g., `host_log_config_metadata(config_id, metadata_key, metadata_value)`) or if the JSON string is acceptable.

4. **Derived columns**: `host_type` (attacker, server, employee, external) and `network_zone` (internal, DMZ, external) are derivable from `groups` but are not raw data. They belong in normalization as computed columns, a lookup table, or a view.

5. **timezone**: Constant `UTC` across all 22 hosts. May be dropped if it adds no discriminating value.