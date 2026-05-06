-- audit_proctitle_event
-- Subtype for PROCTITLE events.
-- 3NF: PK = event_id; single non-key (proctitle) depends only on event_id.
-- Expected rows: 8 (4 intranet + 4 internal_share)

CREATE TABLE audit_proctitle_event (
    event_id   INTEGER  PRIMARY KEY REFERENCES audit_event(event_id),
    proctitle  TEXT     -- hex-encoded command line
);