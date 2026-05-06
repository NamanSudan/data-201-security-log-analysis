-- stg_attack_label_line_raw: Merged table for all 8 label JSONL files (61,862 rows)
-- labels_json and rules_json stored as TEXT (1NF violation, deferred to 3NF junction tables)
-- Candidate key: (source_host, source_log, line_number)
-- Reference snapshot - canonical schema is in src/models/staging/labels.py

CREATE TABLE stg_attack_label_line_raw (
    row_id          SERIAL PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,         -- YAML host_key, e.g. "inet-firewall"
    source_log      VARCHAR(50) NOT NULL,         -- log filename, e.g. "dnsmasq.log"
    line_number     INTEGER NOT NULL,             -- line in the annotated raw log file
    labels_json     TEXT NOT NULL,                -- JSON array of 2-4 label strings
    rules_json      TEXT NOT NULL                 -- JSON dict mapping labels to rule arrays
);