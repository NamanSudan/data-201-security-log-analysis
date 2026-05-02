-- =====================================================================
-- Question: Within the initial_access lead-in and the
--           privilege_escalation climax, which detection rule fires
--           the most for each individual label?
-- Story role: connects the two main story phases. Foothold (in
--             initial_access) is dominated by a single high-volume
--             rule, while the privilege_escalation labels each have
--             a different best-coverage rule. The "top rule per
--             label" lens makes that contrast explicit.
-- SQL concepts: CTE, INNER JOIN (3 tables), aggregation, top-N per
--               group via ROW_NUMBER OVER PARTITION BY, GROUP BY.
-- Expected result: roughly 7 rows, one per (phase, label) inside the
--                  two story phases, each showing the single
--                  best-firing rule for that label.
-- Recommendation: report (rule-coverage subsection) and Q&A backup.
--                 Optional deck slide if a rule-coverage matrix is
--                 wanted.
-- =====================================================================

WITH rule_per_label AS (
    SELECT ap.phase_name,
           al.label_id,
           al.label_name,
           llr.rule_name,
           COUNT(*) AS times_triggered,
           ROW_NUMBER() OVER (
               PARTITION BY al.label_id
               ORDER BY COUNT(*) DESC, llr.rule_name
           ) AS rule_rank_in_label
    FROM labeled_line_rule llr
    JOIN attack_label al ON al.label_id = llr.label_id
    JOIN attack_phase ap ON ap.phase_id = al.phase_id
    WHERE ap.phase_name IN ('initial_access', 'privilege_escalation')
    GROUP BY ap.phase_name, al.label_id, al.label_name, llr.rule_name
)
SELECT phase_name,
       label_name,
       rule_name,
       times_triggered
FROM rule_per_label
WHERE rule_rank_in_label = 1
ORDER BY phase_name, times_triggered DESC, label_name;
