-- =====================================================================
-- Question: Within the privilege_escalation phase only, which detection
--           rules catch the most labeled lines, and how do the
--           audit-domain rules rank against the higher-volume host and
--           DNS rules that observe the same attack?
-- Story role: privilege_escalation climax. Story-aligned variant of the
--             broader rule-effectiveness query in
--             naman_advanced_queries.sql Q2. Restricting to one phase
--             keeps the deck slide readable and lets the audit-rule
--             ranking (which catches the actual su+sudo chain) stand
--             out instead of being dwarfed by the dnsteal volume.
-- SQL concepts: CTE, INNER JOIN (3 tables), DENSE_RANK window, COUNT
--               DISTINCT, GROUP BY, ORDER BY.
-- Expected result: roughly 8 to 12 rows, one per detection rule that
--                  fires inside privilege_escalation, with line counts,
--                  label counts, and an effectiveness rank.
-- Recommendation: report (rule effectiveness table) and Q&A backup.
--                 Optional deck slide if a rule-detail view is wanted.
-- =====================================================================

WITH rule_stats AS (
    SELECT llr.rule_name,
           COUNT(DISTINCT llr.labeled_line_id) AS lines_triggered,
           COUNT(DISTINCT llr.label_id)        AS labels_triggered
    FROM labeled_line_rule llr
    JOIN attack_label al ON al.label_id = llr.label_id
    JOIN attack_phase ap ON ap.phase_id = al.phase_id
    WHERE ap.phase_name = 'privilege_escalation'
    GROUP BY llr.rule_name
)
SELECT rule_name,
       lines_triggered,
       labels_triggered,
       DENSE_RANK() OVER (ORDER BY lines_triggered DESC) AS effectiveness_rank
FROM rule_stats
ORDER BY effectiveness_rank, rule_name;
