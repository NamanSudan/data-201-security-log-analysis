-- audit_event
-- Supertype table. One row per raw audit log line.
-- Natural unique key: (host_id, line_number).
-- 3NF: PK = event_id; every non-key attribute depends only on event_id.
-- host_id is an FK to the separate host entity (no transitive dependency).
-- Expected rows: 3,048

CREATE TABLE audit_event (
    event_id    SERIAL                   PRIMARY KEY,
    host_id     INTEGER                  NOT NULL REFERENCES host(host_id),
    line_number INTEGER                  NOT NULL,
    raw_line    TEXT                     NOT NULL,
    type        VARCHAR(20)              NOT NULL,
    epoch       DOUBLE PRECISION         NOT NULL,
    serial      INTEGER                  NOT NULL,
    timestamp   TIMESTAMPTZ              NOT NULL,
    pid         INTEGER,
    uid         INTEGER,
    auid        BIGINT,                  -- 4294967295 = unset sentinel
    ses         BIGINT,                  -- 4294967295 = unset sentinel

    CONSTRAINT uq_audit_event_host_line UNIQUE (host_id, line_number)
);