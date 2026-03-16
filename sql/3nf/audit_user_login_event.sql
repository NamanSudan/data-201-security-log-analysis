-- audit_user_login_event
-- Subtype for USER_LOGIN.
-- Primary msg-derived attributes: terminal (e.g. /dev/pts/0), id (uid, e.g. 1002),
-- exe, hostname, addr -- join audit_message on event_id.
-- Note: terminal here is the msg-embedded field, distinct from LOGIN's top-level tty.
-- 3NF: single-column key (event_id); no other attributes.
-- Expected rows: 3 (all intranet_server)

CREATE TABLE audit_user_login_event (
    event_id  INTEGER  PRIMARY KEY REFERENCES audit_event(event_id)
);
