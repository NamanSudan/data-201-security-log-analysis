-- labeled_line_rule: Junction (line, label, rule_name); one row per rule per label per line
-- 1NF resolution of rules_json. rule_name kept as string; optional rule table later.
-- Depends on: labeled_line, attack_label. DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE labeled_line_rule (
    labeled_line_id INT NOT NULL REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    label_id        INT NOT NULL REFERENCES attack_label(label_id),
    rule_name       VARCHAR(120) NOT NULL,
    PRIMARY KEY (labeled_line_id, label_id, rule_name)
);
