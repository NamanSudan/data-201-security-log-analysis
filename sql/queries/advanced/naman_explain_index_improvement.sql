-- =====================================================================
-- Advanced query: incident response zoom-in on intranet_server, with
-- a documented EXPLAIN ANALYZE before/after improvement from a new
-- composite index.
--
-- Question: during the privilege-escalation window on
-- 2022-01-24, what audit events fired on intranet_server between
-- 04:37:30 and 04:38:15 UTC, with their PAM message payload?
--
-- Why this query: this is the classic incident-response pattern. An
-- analyst knows roughly when something went wrong (e.g. from a SIEM
-- alert) and zooms into a narrow time window on a specific host. The
-- query benefits the most from an index designed for that access
-- pattern: (host_id, timestamp).
--
-- Index added (see sql/3nf/_indexes.sql):
--   CREATE INDEX idx_audit_event_host_timestamp
--     ON audit_event (host_id, timestamp);
--
-- Note: idx_audit_event_host_timestamp is created and dropped by
-- Alembic migration 742e860d116f (see
-- alembic/versions/20260501_1946_742e860d116f_add_privilege_escalation_index_and_.py).
-- Normal users should not run any DROP INDEX or CREATE INDEX
-- statement against this index from psql or pgAdmin. The Alembic
-- migration is the only supported lifecycle path. The before and
-- after plans recorded below are captured evidence; the
-- reproduction instructions in each block use Alembic commands,
-- not manual DDL.
-- =====================================================================

-- The query itself (run this to see the 9-row privilege-escalation chain).
SELECT ae.timestamp,
       ae.type,
       am.op    AS pam_operation,
       am.acct  AS target_account,
       am.exe   AS executable,
       am.terminal
FROM audit_event ae
JOIN host h                ON h.host_id    = ae.host_id
LEFT JOIN audit_message am ON am.event_id = ae.event_id
WHERE h.host_key = 'intranet_server'
  AND ae.timestamp BETWEEN '2022-01-24 04:37:30+00'::timestamptz
                       AND '2022-01-24 04:38:15+00'::timestamptz
ORDER BY ae.timestamp;

-- =====================================================================
-- EXPLAIN ANALYZE evidence captured 2026-05-01 against the loaded
-- russellmitchell slice (3,048 audit events).
-- =====================================================================

-- BEFORE (no idx_audit_event_host_timestamp present):
-- The plan below is captured evidence; do not regenerate it by
-- running DROP INDEX in psql or pgAdmin. To reproduce the
-- baseline in an isolated local DB:
--   1. alembic -c alembic/alembic.ini downgrade -1
--      (rolls migration 742e860d116f back, removing the index
--      and the v_privilege_escalation_timeline view; only do
--      this on a throwaway DB)
--   2. ANALYZE audit_event;
--   3. EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query above>;
--
--                                                                          QUERY PLAN
-- ---------------------------------------------------------------------------------------------------------------------------------------------
-- Sort  (cost=171.22..171.22 rows=1 width=43) (actual time=1.138..1.224 rows=9 loops=1)
--   Sort Key: ae."timestamp"
--   Sort Method: quicksort  Memory: 25kB
--   Buffers: shared hit=141
--   ->  Nested Loop Left Join  (cost=0.42..171.21 rows=1 width=43) (actual time=0.638..1.119 rows=9 loops=1)
--         ->  Nested Loop  (cost=0.14..162.91 rows=1 width=21) (actual time=0.598..1.073 rows=9 loops=1)
--               Join Filter: (ae.host_id = h.host_id)
--               ->  Index Scan using host_host_key_key on host h
--                     Index Cond: ((host_key)::text = 'intranet_server'::text)
--               ->  Seq Scan on audit_event ae  (actual time=0.558..0.946 rows=9 loops=1)
--                     Filter: ((timestamp >= ...) AND (timestamp <= ...))
--                     Rows Removed by Filter: 3039
--         ->  Index Scan using audit_message_pkey on audit_message am
-- Planning Time: 3.401 ms
-- Execution Time: 1.462 ms

-- AFTER (with idx_audit_event_host_timestamp on (host_id, timestamp)):
-- The plan below is captured evidence; do not regenerate it by
-- running CREATE INDEX in psql or pgAdmin. After the BEFORE
-- benchmark on the throwaway DB, restore the index and the view
-- by running:
--   1. alembic -c alembic/alembic.ini upgrade head
--      (re-applies migration 742e860d116f, recreating
--      idx_audit_event_host_timestamp and
--      v_privilege_escalation_timeline)
--   2. ANALYZE audit_event;
--   3. EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query above>;
--
--                                                                                              QUERY PLAN
-- -----------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Sort  (cost=24.79..24.79 rows=1 width=43) (actual time=0.306..0.315 rows=9 loops=1)
--   Sort Key: ae."timestamp"
--   Sort Method: quicksort  Memory: 25kB
--   Buffers: shared hit=33 read=2
--   ->  Nested Loop Left Join  (cost=0.70..24.78 rows=1 width=43) (actual time=0.236..0.267 rows=9 loops=1)
--         ->  Nested Loop  (cost=0.42..16.47 rows=1 width=21) (actual time=0.158..0.172 rows=9 loops=1)
--               ->  Index Scan using host_host_key_key on host h
--                     Index Cond: ((host_key)::text = 'intranet_server'::text)
--               ->  Index Scan using idx_audit_event_host_timestamp on audit_event ae
--                     Index Cond: ((host_id = h.host_id)
--                                  AND ("timestamp" >= '2022-01-24 04:37:30+00')
--                                  AND ("timestamp" <= '2022-01-24 04:38:15+00'))
--         ->  Index Scan using audit_message_pkey on audit_message am
-- Planning Time: 4.245 ms
-- Execution Time: 0.640 ms

-- =====================================================================
-- Summary:
--   Execution Time: 1.462 ms -> 0.640 ms (about 2.3x faster).
--   Plan node: Seq Scan (3039 rows discarded) -> Index Scan
--     (Index Cond covers both the host_id equality and the
--     timestamp BETWEEN range).
--   Buffers touched: 141 -> 33 (almost 4x less).
--   Cost estimate: 171.22 -> 24.79.
--
-- The improvement scales with audit_event row count. In the russell
-- mitchell slice the table is small enough that the absolute time is
-- already low, but the planner-statistic shift (cost 171 -> 25) shows
-- the same proportional win that would be felt on the full corpus
-- (across all five testbeds, audit_event would be roughly 5x larger).
-- =====================================================================
