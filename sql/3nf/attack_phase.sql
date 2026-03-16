-- attack_phase: Lookup for 7 attack phases (3NF; no FKs)
-- Seed from project taxonomy (docs/data_exploration/notebook_findings/naman_labels_findings.md).
-- DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE attack_phase (
    phase_id   SERIAL PRIMARY KEY,
    phase_name VARCHAR(50) NOT NULL UNIQUE
);
