-- =====================================================================
-- Question: Within the privilege_escalation phase on intranet_server,
--           how many audit events of each type fire, and when does
--           each type first and last appear during the chain?
-- Story role: privilege_escalation climax. Counts the audit-event
--             types that participate in the su then sudo chain on
--             intranet_server and adds the timing envelope that drives
--             a bar chart on the dashboard and on slide 8 of the final
--             presentation. Where
--             ishaan_audit_types_in_privilege_escalation.sql returns
--             just the catalog (DISTINCT type), this query adds
--             event_count, first_seen, last_seen, and a RANK over
--             event_count so a chart can sort the bars by frequency.
-- SQL concepts: Subquery with EXISTS (correlated to the outer
--               audit_event row, identical join body to the original
--               Ishaan query), aggregation (COUNT, MIN, MAX), and a
--               window function (RANK) for downstream ordering.
-- Expected result: 8 rows on the russellmitchell slice (one per
--                  distinct audit_type that fires on the privilege
--                  escalation chain). USER_START appears twice across
--                  the chain (event_count = 2, type_rank = 1); the
--                  other seven types each fire once and tie at
--                  type_rank = 2. first_seen and last_seen sit inside
--                  the 2022-01-24 04:37:40 to 04:38:06 UTC window.
-- Recommendation: deck slide 8 (Ishaan EXISTS deep dive) and dashboard
--                 panel 6 (bar chart of event_count by audit_type).
--                 The chip catalog in panel 6 still reads from
--                 ishaan_audit_types_in_privilege_escalation.sql, so
--                 the two Ishaan EXISTS queries appear side by side.
-- =====================================================================

SELECT ae.type                              AS audit_type,
       COUNT(*)                             AS event_count,
       MIN(ae.timestamp)                    AS first_seen,
       MAX(ae.timestamp)                    AS last_seen,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS type_rank
FROM audit_event ae
JOIN host h ON h.host_id = ae.host_id
WHERE h.host_key = 'intranet_server'
  AND EXISTS (
      SELECT 1
      FROM labeled_line ll
      JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
      JOIN attack_label al        ON al.label_id = lll.label_id
      JOIN attack_phase ap        ON ap.phase_id = al.phase_id
      WHERE ll.source_host = h.host_key
        AND ll.source_log  = 'audit.log'
        AND ll.line_number = ae.line_number
        AND ap.phase_name  = 'privilege_escalation'
  )
GROUP BY ae.type
ORDER BY event_count DESC, audit_type;
