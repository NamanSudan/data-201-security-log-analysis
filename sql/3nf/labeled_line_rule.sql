-- labeled_line_rule: Junction (line, label, rule_name); one row per rule per label per line
-- 1NF resolution of rules_json. rule_name kept as string; optional rule table later.
-- Depends on: labeled_line, labeled_line_label, attack_label.
-- Composite FK to labeled_line_label ensures a rule can only exist for
-- a (line, label) pair that is already in the label assignment junction.
-- DDL reference: docs/schema/labels_normalization_staging_to_3nf.md

CREATE TABLE labeled_line_rule (
    labeled_line_id INT NOT NULL,
    label_id        INT NOT NULL,
    rule_name       VARCHAR(120) NOT NULL,
    PRIMARY KEY (labeled_line_id, label_id, rule_name),
    FOREIGN KEY (labeled_line_id) REFERENCES labeled_line(labeled_line_id) ON DELETE CASCADE,
    FOREIGN KEY (labeled_line_id, label_id) REFERENCES labeled_line_label(labeled_line_id, label_id)
);