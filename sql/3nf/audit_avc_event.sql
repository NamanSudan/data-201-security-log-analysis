-- audit_avc_event
-- Subtype for AVC events.
-- 3NF: PK = event_id; every non-key attribute depends only on event_id.
-- No partial or transitive dependency.
-- Expected rows: 8 (4 intranet + 4 internal_share)

CREATE TABLE audit_avc_event (
    event_id   INTEGER      PRIMARY KEY REFERENCES audit_event(event_id),
    apparmor   VARCHAR(20), -- AppArmor subsystem
    operation  VARCHAR(30), -- e.g. profile_replace
    profile    VARCHAR(50),
    name       TEXT,        -- resource name
    info       TEXT,        -- additional info
    comm       VARCHAR(50)
);