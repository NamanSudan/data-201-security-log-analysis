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
-- Run with:
--   DROP INDEX IF EXISTS idx_audit_event_host_timestamp;
--   ANALYZE audit_event;
--   EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query above>;
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
-- Run with:
--   CREATE INDEX idx_audit_event_host_timestamp ON audit_event (host_id, timestamp);
--   ANALYZE audit_event;
--   EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query above>;
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
