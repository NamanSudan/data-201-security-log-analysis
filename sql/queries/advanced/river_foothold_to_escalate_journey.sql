-- =====================================================================
-- Question: How does the attacker's foothold-then-escalate progression
--           on intranet_server look when the labeled web-access lines
--           are bucketed into thirds by line position? Where in that
--           journey do the privilege_escalation traces appear?
-- Story role: initial_access lead-in. The bulk of foothold evidence
--             lives on intranet_server/access.log.2 (7,691 lines).
--             A handful of privilege_escalation labels also fall on
--             that same log. Bucketing by line_number into thirds
--             surfaces where the foothold web traffic is densest and
--             where the escalation activity sits relative to it.
-- SQL concepts: CTE, INNER JOIN (3 tables), NTILE window function,
--               GROUP BY, MIN, MAX, COUNT.
-- Expected result: roughly 4 to 6 rows, one per (journey_third, phase),
--                  showing how foothold and privilege_escalation labels
--                  distribute across the early/mid/late thirds of
--                  access.log.2.
-- Recommendation: report (lead-in section) and optional deck slide if
--                 the progression chart reads well.
-- =====================================================================

WITH access_labels AS (
    SELECT ll.line_number,
           al.label_name,
           ap.phase_name,
           NTILE(3) OVER (ORDER BY ll.line_number) AS journey_third
    FROM labeled_line ll
    JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
    JOIN attack_label al        ON al.label_id = lll.label_id
    JOIN attack_phase ap        ON ap.phase_id = al.phase_id
    WHERE ll.source_host = 'intranet_server'
      AND ll.source_log  = 'access.log.2'
      AND ap.phase_name IN ('initial_access', 'privilege_escalation')
)
SELECT journey_third,
       phase_name,
       label_name,
       COUNT(*)         AS labeled_lines,
       MIN(line_number) AS first_line,
       MAX(line_number) AS last_line
FROM access_labels
GROUP BY journey_third, phase_name, label_name
ORDER BY journey_third, phase_name, label_name;
