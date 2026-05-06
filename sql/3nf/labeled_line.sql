-- labeled_line: One row per (source_host, source_log, line_number); 61,862 rows
-- Provenance for joining to host/audit; surrogate PK for simpler FKs in junctions.
-- DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE labeled_line (
    labeled_line_id SERIAL PRIMARY KEY,
    source_host      VARCHAR(30) NOT NULL,
    source_log       VARCHAR(50) NOT NULL,
    line_number      INTEGER NOT NULL,
    UNIQUE (source_host, source_log, line_number)
);