-- audit_login_event
-- Subtype for LOGIN events.
-- 3NF: PK = event_id; every non-key (old_auid, old_ses, tty, res)
-- depends only on event_id. No partial or transitive dependency.
-- Expected rows: 410 (304 intranet + 106 internal_share)

CREATE TABLE audit_login_event (
    event_id  INTEGER      PRIMARY KEY REFERENCES audit_event(event_id),
    old_auid  BIGINT,      -- often 4294967295 sentinel
    old_ses   BIGINT,      -- often 4294967295 sentinel
    tty       VARCHAR(30), -- e.g. "(none)"
    res       VARCHAR(10)  -- e.g. "1" (success)
);