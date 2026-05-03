-- =====================================================================
-- Performance indexes for the security-logs 3NF schema.
--
-- ###  CANONICAL DDL ONLY  ###
-- This file is the source-of-truth for which indexes the workload needs.
-- It is NOT the runtime application path. The actual creation must go
-- through a new Alembic migration (op.create_index in upgrade,
-- op.drop_index in downgrade) so every developer's local DB stays in
-- sync. See alembic/versions/ for the existing migration chain.
--
-- Status (2026-05-01): the index below is managed by Alembic. Migration
-- 20260501_1946_742e860d116f_add_privilege_escalation_index_and_.py
-- (revision 742e860d116f) creates it in upgrade and drops it in
-- downgrade. Run alembic -c alembic/alembic.ini upgrade head to apply.
-- =====================================================================

-- Index 1: Composite (host_id, timestamp) on audit_event.
--
-- Motivating workload: incident-response queries that zoom in on a
-- specific host within a narrow time window (e.g. "what happened on
-- intranet_server between 04:37 and 04:38 UTC on 2022-01-24"). Without
-- this index the planner does a Seq Scan on audit_event (3,048 rows)
-- and applies the timestamp filter row-by-row, even though the existing
-- uq_audit_event_host_line index can narrow on host but not on
-- timestamp. EXPLAIN ANALYZE evidence:
--
--   Before: Seq Scan on audit_event, 3039 rows removed by filter,
--           Execution Time: 1.462 ms
--   After:  Index Scan using idx_audit_event_host_timestamp,
--           Execution Time: 0.640 ms (about 2.3x faster)
--
-- See sql/queries/advanced/naman_explain_index_improvement.sql for the
-- full EXPLAIN output and the demonstration query.
CREATE INDEX IF NOT EXISTS idx_audit_event_host_timestamp
    ON audit_event (host_id, timestamp);

-- ANALYZE so the planner picks up updated statistics immediately.
ANALYZE audit_event;
