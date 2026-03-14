-- stg_host_log_config_raw: One row per log config entry per host (66 rows)
-- Source: servers.yaml "logs" nested field (1-9 configs per host)
-- FK to stg_host_raw.host_id
-- Reference snapshot -- canonical schema is in src/models/staging/host.py

CREATE TABLE stg_host_log_config_raw (
    config_id       SERIAL PRIMARY KEY,
    host_id         INT NOT NULL REFERENCES stg_host_raw(host_id),
    log_path        TEXT NOT NULL,                -- e.g. "/var/log/audit/audit.log"
    log_type        VARCHAR(50) NOT NULL,         -- 11 distinct log types
    codec           TEXT,                         -- string or serialized JSON dict
    file_chunk_size INT,
    add_field_json  TEXT                          -- serialized JSON string
);
