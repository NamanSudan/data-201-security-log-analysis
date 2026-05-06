-- audit_user_cmd_event
-- Subtype for USER_CMD.
-- Primary msg-derived attributes: cmd (hex-encoded command), cwd (working directory),
-- terminal, res -- join audit_message on event_id.
-- 3NF: single-column key (event_id); no other attributes.
-- Expected rows: 1 (intranet_server only)

CREATE TABLE audit_user_cmd_event (
    event_id  INTEGER  PRIMARY KEY REFERENCES audit_event(event_id)
);