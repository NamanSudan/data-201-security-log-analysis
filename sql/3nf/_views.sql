-- =====================================================================
-- Saved views.
--
-- ###  CANONICAL DDL ONLY  ###
-- This file is the source-of-truth for which analytical views the
-- project relies on. It is NOT the runtime application path. The actual
-- creation must go through a new Alembic migration (op.execute or a raw
-- SQL block in upgrade, with the matching DROP VIEW in downgrade) so
-- every developer's local DB stays in sync.
--
-- Status (2026-05-01): the view below was created manually in psql
-- against the local dev DB for testing only. It must be either
--   (a) converted to an Alembic migration, or
--   (b) dropped before final submission.
-- See WORK_HANDOVER_NEXT_SESSION.md for the migration scaffold.
-- =====================================================================

-- View: v_privilege_escalation_timeline
--
-- Purpose: collapse the cross-domain join used by the privilege
-- escalation analysis (audit_event + audit_message + host +
-- labeled_line + labeled_line_label + attack_label + attack_phase) into
-- a single virtual relation. Dashboard charts and ad hoc investigation
-- queries can SELECT * FROM v_privilege_escalation_timeline WHERE ...
-- without re-typing the seven-table join every time.
--
-- Row grain: one row per audit event that has a privilege_escalation
-- label.
--
-- Returns 9 rows on the russellmitchell slice (the su + sudo chain on
-- intranet_server at 2022-01-24 04:37:40 to 04:38:06 UTC).
CREATE OR REPLACE VIEW v_privilege_escalation_timeline AS
SELECT h.host_key,
       ae.event_id,
       ae.timestamp,
       ae.type                 AS audit_type,
       am.op                   AS pam_operation,
       am.acct                 AS target_account,
       am.exe                  AS executable,
       am.terminal,
       string_agg(DISTINCT al.label_name, ', '
                  ORDER BY al.label_name) AS labels,
       string_agg(DISTINCT llr.rule_name, ', '
                  ORDER BY llr.rule_name) AS rules
FROM audit_event ae
JOIN host h               ON h.host_id = ae.host_id
JOIN labeled_line ll      ON ll.source_host = h.host_key
                         AND ll.source_log  = 'audit.log'
                         AND ll.line_number = ae.line_number
JOIN labeled_line_label lll ON lll.labeled_line_id = ll.labeled_line_id
JOIN attack_label al      ON al.label_id = lll.label_id
JOIN attack_phase ap      ON ap.phase_id = al.phase_id
LEFT JOIN audit_message am ON am.event_id = ae.event_id
LEFT JOIN labeled_line_rule llr
       ON llr.labeled_line_id = ll.labeled_line_id
      AND llr.label_id        = al.label_id
WHERE ap.phase_name = 'privilege_escalation'
GROUP BY h.host_key, ae.event_id, ae.timestamp, ae.type,
         am.op, am.acct, am.exe, am.terminal;
