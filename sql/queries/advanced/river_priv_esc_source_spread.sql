-- =====================================================================
-- Question: How does privilege_escalation evidence spread across the
--           five different log sources that observed the attack?
-- Story role: privilege_escalation climax (breadth view). The deep
--             nine-event chain is captured in audit.log on
--             intranet_server, but the same 82-line attack also
--             leaves traces on auth.log, access.log.2 (same host),
--             and on cpu.log and dnsmasq.log on other hosts. This
--             query confirms that the database lets us see the
--             attack from five different vantage points.
-- SQL concepts: CTE, INNER JOIN (3 tables), COUNT DISTINCT, RANK
--               window, GROUP BY.
-- Expected result: 5 rows, one per (source_host, source_log) pair
--                  carrying privilege_escalation labels, ordered by
--                  volume rank.
-- Recommendation: report (privilege_escalation breadth subsection)
--                 and Q&A backup. Optional deck slide if a
--                 cross-source coverage chart is wanted.
-- =====================================================================

WITH source_evidence AS (
    SELECT ll.source_host,
           ll.source_log,
           COUNT(DISTINCT lll.labeled_line_id) AS labeled_lines,
           COUNT(DISTINCT al.label_id)         AS distinct_labels
    FROM labeled_line ll
    JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
    JOIN attack_label al        ON al.label_id = lll.label_id
    JOIN attack_phase ap        ON ap.phase_id = al.phase_id
    WHERE ap.phase_name = 'privilege_escalation'
    GROUP BY ll.source_host, ll.source_log
)
SELECT source_host,
       source_log,
       labeled_lines,
       distinct_labels,
       RANK() OVER (ORDER BY labeled_lines DESC) AS volume_rank
FROM source_evidence
ORDER BY volume_rank, source_host;
