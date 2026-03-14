-- stg_host_raw: One row per host machine (22 rows)
-- Source: russellmitchell/processing/config/servers.yaml
-- Multi-valued fields stored as JSON-array strings in TEXT (1NF deferred)
-- Reference snapshot -- canonical schema is in src/models/staging/host.py

CREATE TABLE stg_host_raw (
    host_id              SERIAL PRIMARY KEY,
    host_key             VARCHAR(50) NOT NULL UNIQUE,
    hostname             VARCHAR(100) NOT NULL UNIQUE,
    groups               TEXT NOT NULL,            -- JSON array string, e.g. ["adm","sudo"]
    username             VARCHAR(50),              -- only 7 employee hosts
    openvpn_user         VARCHAR(50),              -- only 3 remote employees
    distribution         VARCHAR(50) NOT NULL,     -- "Ubuntu" or "Debian"
    distribution_release VARCHAR(20) NOT NULL,     -- "bionic" or "stretch"
    distribution_version VARCHAR(20) NOT NULL,     -- "18.04" or "9.11"
    default_ipv4_address VARCHAR(45) NOT NULL,
    default_ipv6_address VARCHAR(45) NOT NULL,
    ipv4_addresses       TEXT NOT NULL,            -- JSON array string
    ipv6_addresses       TEXT NOT NULL,            -- JSON array string
    fqdns                TEXT,                     -- JSON array string; NULL when no FQDNs
    timezone             VARCHAR(10) NOT NULL      -- "UTC" for all 22 hosts
);
