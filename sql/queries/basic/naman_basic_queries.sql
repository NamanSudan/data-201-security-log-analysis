-- Q1: What is the baseline service activity on monitored hosts?
-- Technique:  INNER JOIN (4 tables), CASE inside SUM, GROUP BY
-- Rationale: Establishes normal service behavior so anomalies stand out.
-- The exfiltration service "put" on internal_share is a single start/stop
-- amid hundreds of routine cron jobs.

SELECT h.host_key,
       am.unit   AS service_name,
       SUM(CASE WHEN ae.type = 'SERVICE_START' THEN 1 ELSE 0 END) AS starts,
       SUM(CASE WHEN ae.type = 'SERVICE_STOP'  THEN 1 ELSE 0 END) AS stops
FROM audit_event ae
JOIN audit_service_event ase ON ase.event_id = ae.event_id
JOIN audit_message am        ON am.event_id  = ae.event_id
JOIN host h                  ON h.host_id    = ae.host_id
GROUP BY h.host_key, am.unit
ORDER BY h.host_key,
         SUM(CASE WHEN ae.type = 'SERVICE_START' THEN 1 ELSE 0 END)
       + SUM(CASE WHEN ae.type = 'SERVICE_STOP'  THEN 1 ELSE 0 END) DESC;

-- Results: 33 rows. phpsessionclean dominates intranet_server (384 events).
-- The "put" service on internal_share (1 start, 1 stop) is the exfiltration
-- service.


-- Q2: Where does the attack leave the most evidence across log sources?
-- Technique: INNER JOIN (4 tables), GROUP BY, COUNT DISTINCT, ORDER BY
-- Rationale: Shows which attack phases create the most labeled evidence
-- and across how many different log sources. Privilege escalation spans
-- 5 log sources despite only 82 lines.

SELECT ap.phase_name,
       COUNT(DISTINCT lll.labeled_line_id)                       AS labeled_lines,
       COUNT(DISTINCT ll.source_host || '/' || ll.source_log)    AS log_sources_affected
FROM attack_phase ap
JOIN attack_label al    ON al.phase_id  = ap.phase_id
JOIN labeled_line_label lll ON lll.label_id = al.label_id
JOIN labeled_line ll    ON ll.labeled_line_id = lll.labeled_line_id
GROUP BY ap.phase_name
ORDER BY labeled_lines DESC;

-- Results: Exfiltration dominates (53K lines, 2 sources), but
-- privilege_escalation spans 5 log sources despite only 82 lines.
