-- host_log_config: Per-host log collection configuration (66 rows)
-- Weak entity identified by (host_id, log_path). add_field_json retained as opaque JSON.
-- Reference snapshot - canonical schema is in src/models/final/host.py

CREATE TABLE host_log_config (
    config_id       SERIAL PRIMARY KEY,
    host_id         INT NOT NULL REFERENCES host(host_id),
    log_path        TEXT NOT NULL,
    log_type        VARCHAR(50) NOT NULL,
    codec           TEXT,
    file_chunk_size INT,
    add_field_json  TEXT,
    UNIQUE (host_id, log_path)
);