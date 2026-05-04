-- =====================================================================
-- Question: On the host that carries the attack chain, which audit-event
--           day was the busiest, and where does the attack day rank?
-- Story role: bridges initial_access lead-in into privilege_escalation
--             climax. By focusing on intranet_server alone (host of the
--             attack) and ranking days by raw audit-event volume, we
--             confirm 2022-01-24 as the active day.
-- SQL concepts: INNER JOIN (2 tables), DATE() truncation, RANK window
--               function, GROUP BY, COUNT.
-- Expected result: 4 rows, one per day in the russellmitchell window
--                  (2022-01-21 through 2022-01-24), with event counts
--                  and a rank.
-- Recommendation: report (recap and bridging context) and Q&A. Optional
--                 supporting slide before the climax deep-dive.
-- =====================================================================

SELECT DATE(ae.timestamp) AS event_date,
       COUNT(*)           AS events_that_day,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS day_rank
FROM audit_event ae
JOIN host h ON h.host_id = ae.host_id
WHERE h.host_key = 'intranet_server'
GROUP BY DATE(ae.timestamp)
ORDER BY day_rank, event_date;
