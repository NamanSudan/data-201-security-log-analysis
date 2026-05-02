WITH rule_counts AS (
    SELECT ll.source_host,
           llr.rule_name,
           COUNT(*) AS rule_hits
    FROM labeled_line ll
    INNER JOIN labeled_line_rule llr ON llr.labeled_line_id = ll.labeled_line_id
    GROUP BY ll.source_host, llr.rule_name
),
ranked AS (
    SELECT source_host,
           rule_name,
           rule_hits,
           ROW_NUMBER() OVER (
               PARTITION BY source_host
               ORDER BY rule_hits DESC, rule_name
           ) AS rank_in_host
    FROM rule_counts
)
SELECT source_host,
       rule_name,
       rule_hits,
       rank_in_host
FROM ranked
WHERE rank_in_host <= 5
ORDER BY source_host, rank_in_host;