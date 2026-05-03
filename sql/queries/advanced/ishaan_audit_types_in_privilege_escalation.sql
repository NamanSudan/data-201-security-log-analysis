-- =====================================================================
-- Question: Which audit event types appear on the same intranet_server
--           lines that carry a privilege_escalation label?
-- Story role: privilege_escalation climax. Anchors the attack narrative
--             to the audit-event taxonomy (USER_AUTH, USER_ACCT,
--             CRED_REFR, USER_CMD, etc.) and shows that the su+sudo
--             chain triggers a specific subset of audit types, not
--             arbitrary ones.
-- SQL concepts: Subquery with EXISTS (correlated to the outer
--               audit_event row), DISTINCT, INNER JOIN (4 tables in
--               the EXISTS body), ORDER BY.
-- Expected result: roughly 4 distinct audit_event types
--                  (the exact set comes from the 9 audit events that
--                  carry privilege_escalation labels).
-- Recommendation: report (audit-type-coverage paragraph) and Q&A
--                 backup. Optional deck slide as a one-line
--                 supporting fact.
-- =====================================================================

SELECT DISTINCT ae.type AS audit_type
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
ORDER BY audit_type;
