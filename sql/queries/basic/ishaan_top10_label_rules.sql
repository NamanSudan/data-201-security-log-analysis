SELECT rule_name, COUNT(*) AS times_used
FROM labeled_line_rule
GROUP BY rule_name
ORDER BY times_used DESC
LIMIT 10;
