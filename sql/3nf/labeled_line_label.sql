-- labeled_line_label: Junction line <-> label (~184,517 rows)
-- 1NF resolution of labels_json. Depends on: labeled_line, attack_label.
-- DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE labeled_line_label (
    labeled_line_id INT NOT NULL REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    label_id        INT NOT NULL REFERENCES attack_label(label_id),
    PRIMARY KEY (labeled_line_id, label_id)
);