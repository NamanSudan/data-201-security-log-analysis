-- attack_label: 22 labels with phase_id (resolves FD label_name -> attack_phase)
-- Seed from project taxonomy; label_name unique.
-- Depends on: attack_phase. DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE attack_label (
    label_id   SERIAL PRIMARY KEY,
    label_name VARCHAR(80) NOT NULL UNIQUE,
    phase_id   INT NOT NULL REFERENCES attack_phase(phase_id)
);
