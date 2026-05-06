WITH rule_counts AS (
  SELECT
    label_id,
    rule_name,
    COUNT(*) AS uses
  FROM labeled_line_rule
  GROUP BY label_id, rule_name
),
ranked AS (
  SELECT
    label_id,
    rule_name,
    uses,
    RANK() OVER (PARTITION BY label_id ORDER BY uses DESC) AS rnk
  FROM rule_counts
)
SELECT al.label_name, r.rule_name, r.uses
FROM ranked r
JOIN attack_label al ON al.label_id = r.label_id
WHERE r.rnk = 1
ORDER BY al.label_name;
