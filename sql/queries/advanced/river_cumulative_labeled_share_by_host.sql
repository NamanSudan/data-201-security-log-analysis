WITH host_totals AS (
    SELECT source_host,
           COUNT(*) AS labeled_lines
    FROM labeled_line
    GROUP BY source_host
),
ordered AS (
    SELECT source_host,
           labeled_lines,
           SUM(labeled_lines) OVER (
               ORDER BY labeled_lines DESC
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cum_labeled_lines,
           SUM(labeled_lines) OVER () AS grand_total
    FROM host_totals
)
SELECT source_host,
       labeled_lines,
       ROUND(100.0 * labeled_lines / grand_total, 2) AS pct_of_all_labeled,
       ROUND(100.0 * cum_labeled_lines / grand_total, 2) AS cumulative_pct_of_all_labeled
FROM ordered
ORDER BY labeled_lines DESC;
