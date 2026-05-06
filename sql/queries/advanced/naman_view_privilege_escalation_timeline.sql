-- =====================================================================
-- Question: Show the full nine-event privilege_escalation chain on
--           intranet_server, ordered chronologically, using the saved
--           v_privilege_escalation_timeline view.
-- Story role: privilege_escalation climax. The view collapses the
--             seven-table cross-domain join (audit_event +
--             audit_message + host + labeled_line +
--             labeled_line_label + attack_label + attack_phase +
--             labeled_line_rule) into a single virtual relation. The
--             deck slide reads as a clean audit trail of the attack.
-- SQL concepts: View-based query against v_privilege_escalation_timeline
--               (an Alembic-managed saved view, owned by migration
--               742e860d116f and documented in sql/3nf/_views.sql),
--               ORDER BY.
-- Expected result: 9 rows on the russellmitchell slice, one per
--                  privilege_escalation-labeled audit event on
--                  intranet_server, between 2022-01-24 04:37:40 and
--                  04:38:06 UTC. The chain decomposes into burst 1
--                  (su from www-data to jhall) and burst 2
--                  (sudo cat /etc/shadow as jhall).
-- Recommendation: deck deep-dive 2 of 3. The view itself is also a
--                 rubric artifact for the Views SQL category.
-- =====================================================================

SELECT host_key,
       timestamp,
       audit_type,
       pam_operation,
       target_account,
       executable,
       terminal,
       labels,
       rules
FROM v_privilege_escalation_timeline
ORDER BY timestamp, event_id;
