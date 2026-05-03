-- =====================================================================
-- Question: How does foothold evidence accumulate as we walk through
--           access.log.2 line-by-line on intranet_server? Where does
--           the attacker's web traffic concentrate?
-- Story role: initial_access lead-in. A running cumulative total
--             over 1,000-line buckets shows which slice of the log
--             contains the densest foothold activity, which sets up
--             the privilege_escalation climax that follows.
-- SQL concepts: CTE, INNER JOIN (3 tables), aggregate-in-window
--               SUM(COUNT(*)) OVER (running total), GROUP BY,
--               integer-arithmetic bucketing.
-- Expected result: roughly 8 rows, one per 1,000-line bucket of
--                  access.log.2, with foothold counts per bucket and
--                  a cumulative running total that climbs to about
--                  7,691 by the final bucket.
-- Recommendation: report (lead-in cumulative chart). Optional deck
--                 spotlight if a step-curve visualization is wanted.
-- =====================================================================

WITH foothold_lines AS (
    SELECT ll.line_number,
           (ll.line_number / 1000) * 1000 AS line_bucket
    FROM labeled_line ll
    JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
    JOIN attack_label al        ON al.label_id = lll.label_id
    WHERE ll.source_host = 'intranet_server'
      AND ll.source_log  = 'access.log.2'
      AND al.label_name  = 'foothold'
)
SELECT line_bucket,
       COUNT(*)                                  AS foothold_in_bucket,
       SUM(COUNT(*)) OVER (ORDER BY line_bucket) AS foothold_cumulative
FROM foothold_lines
GROUP BY line_bucket
ORDER BY line_bucket;
