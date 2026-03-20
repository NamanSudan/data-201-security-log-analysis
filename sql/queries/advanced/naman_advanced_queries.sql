-- Q1: Can we reconstruct the exact privilege escalation attack sequence?
-- Technique: CTE, 6-table JOIN, ROW_NUMBER window function, string_agg

WITH attack_timeline AS (
    SELECT ae.event_id,
           ae.timestamp,
           ae.type            AS audit_type,
           am.op              AS pam_operation,
           am.acct            AS target_account,
           am.exe             AS executable,
           am.terminal,
           al.label_name,
           ap.phase_name
    FROM audit_event ae
    JOIN host h             ON h.host_id = ae.host_id
    JOIN labeled_line ll    ON ll.source_host = h.host_key
      AND ll.source_log  = 'audit.log'
      AND ll.line_number = ae.line_number
    JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
    JOIN attack_label al    ON al.label_id  = lll.label_id
    JOIN attack_phase ap    ON ap.phase_id  = al.phase_id
    LEFT JOIN audit_message am ON am.event_id = ae.event_id
    WHERE h.host_key = 'intranet_server'
)
SELECT event_id,
       timestamp,
       audit_type,
       pam_operation,
       target_account,
       executable,
       terminal,
       string_agg(label_name, ', ' ORDER BY label_name) AS labels
FROM attack_timeline
GROUP BY event_id, timestamp, audit_type, pam_operation,
         target_account, executable, terminal
ORDER BY timestamp, event_id;

-- Expected: 9 rows showing two distinct attack bursts:
-- Burst 1 (04:37:40 UTC): su from www-data to jhall via /bin/su (4 events)
-- Burst 2 (04:38:06 UTC): sudo cat /etc/shadow via /usr/bin/sudo (5 events)
-- Gap: 25.6 seconds between bursts.


-- Q2: Which detection rules are most effective at identifying the attack?
-- Technique: CTE, JOIN (3 tables), DENSE_RANK window function, GROUP BY

WITH rule_stats AS (
    SELECT llr.rule_name,
           ap.phase_name,
           COUNT(DISTINCT llr.labeled_line_id) AS lines_triggered,
           COUNT(DISTINCT llr.label_id)        AS labels_triggered
    FROM labeled_line_rule llr
    JOIN attack_label al ON al.label_id  = llr.label_id
    JOIN attack_phase ap ON ap.phase_id  = al.phase_id
    GROUP BY llr.rule_name, ap.phase_name
)
SELECT rule_name,
       phase_name,
       lines_triggered,
       labels_triggered,
       DENSE_RANK() OVER (ORDER BY lines_triggered DESC) AS effectiveness_rank
FROM rule_stats
ORDER BY lines_triggered DESC
LIMIT 15;

-- Expected: dnsteal.domain.match is rank 1 (53K lines).
-- Audit-based rules rank lower by volume but catch critical escalation.


-- Q3: Can we trace the attacker's lateral movement across hosts?
-- Technique: CTE, multi-table JOIN (6 tables), COALESCE, ORDER BY timestamp

WITH labeled_audit AS (
    SELECT h.host_key,
           ae.timestamp,
           ae.type                AS audit_type,
           am.acct                AS target_account,
           am.exe                 AS executable,
           am.unit                AS service_unit,
           ap.phase_name,
           string_agg(al.label_name, ', ' ORDER BY al.label_name) AS labels
    FROM audit_event ae
    JOIN host h             ON h.host_id = ae.host_id
    JOIN labeled_line ll    ON ll.source_host = h.host_key
      AND ll.source_log  = 'audit.log'
      AND ll.line_number = ae.line_number
    JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
    JOIN attack_label al    ON al.label_id  = lll.label_id
    JOIN attack_phase ap    ON ap.phase_id  = al.phase_id
    LEFT JOIN audit_message am ON am.event_id = ae.event_id
    GROUP BY h.host_key, ae.timestamp, ae.type,
             am.acct, am.exe, am.unit, ap.phase_name
)
SELECT host_key,
       timestamp,
       audit_type,
       phase_name,
       labels,
       COALESCE(target_account, service_unit, '(n/a)') AS target_detail,
       executable
FROM labeled_audit
ORDER BY timestamp, host_key;

-- Expected: 11 rows across 2 hosts.
-- 04:37-04:38: intranet_server shows privilege_escalation
-- 13:50: internal_share shows exfiltration (put service)
-- ~9 hours apart: escalate on one host, exfiltrate from another.


-- Q4: Can we identify distinct attack bursts from timing patterns?
-- Technique: CTE, LAG + ROW_NUMBER window functions, CASE, EXTRACT

WITH labeled_audit_events AS (
    SELECT ae.event_id,
           ae.timestamp,
           ae.type,
           ROW_NUMBER() OVER (ORDER BY ae.timestamp, ae.line_number) AS seq,
           LAG(ae.timestamp) OVER (ORDER BY ae.timestamp, ae.line_number) AS prev_timestamp
    FROM audit_event ae
    JOIN host h ON h.host_id = ae.host_id
    JOIN labeled_line ll ON ll.source_host = h.host_key
      AND ll.source_log = 'audit.log'
      AND ll.line_number = ae.line_number
    WHERE h.host_key = 'intranet_server'
)
SELECT seq,
       timestamp,
       type,
       EXTRACT(EPOCH FROM timestamp - prev_timestamp) AS seconds_since_prev,
       CASE
           WHEN prev_timestamp IS NULL THEN 'FIRST EVENT'
           WHEN EXTRACT(EPOCH FROM timestamp - prev_timestamp) > 10 THEN 'NEW BURST'
           ELSE 'continuation'
       END AS burst_indicator
FROM labeled_audit_events
ORDER BY seq;

-- Expected: Two distinct bursts.
-- Burst 1 (events 1-4): su to jhall, all within 24ms.
-- Burst 2 (events 5-9): sudo commands, starting 25.6 seconds later.
