-- audit_message
-- Unpacked msg blob; resolves 1NF violation in stg_audit_line_raw.
-- Each of the 12 msg key-value pairs is stored as a separate atomic column.
-- 3NF: PK = event_id (FK to audit_event); every non-key attribute depends
-- only on event_id. Cardinality: 0..1 per audit_event.
-- Expected rows: 2,614 (validated)

CREATE TABLE audit_message (
    event_id  INTEGER       PRIMARY KEY REFERENCES audit_event(event_id),
    op        VARCHAR(30),
    acct      VARCHAR(50),
    exe       TEXT,
    hostname  VARCHAR(50),  -- PAM/msg hostname, not the host entity
    addr      VARCHAR(50),
    terminal  VARCHAR(30),
    res       VARCHAR(20),  -- e.g. "success"
    unit      VARCHAR(100), -- SERVICE_* events
    comm      VARCHAR(50),
    id        INTEGER,      -- USER_LOGIN (uid, e.g. 1002)
    cwd       TEXT,         -- USER_CMD
    cmd       TEXT          -- USER_CMD (hex)
);
