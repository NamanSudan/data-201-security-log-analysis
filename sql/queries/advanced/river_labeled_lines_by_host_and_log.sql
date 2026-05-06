WITH per_source AS (
    SELECT source_host,
           source_log,
           COUNT(*) AS line_count
    FROM labeled_line
    GROUP BY source_host, source_log
),
total AS (
    SELECT SUM(line_count) AS total_count
    FROM per_source
)
SELECT ps.source_host,
       ps.source_log,
       ps.line_count,
       ROUND(100.0 * ps.line_count / t.total_count, 2) AS pct_of_all_labeled
FROM per_source ps
CROSS JOIN total t
ORDER BY ps.line_count DESC;