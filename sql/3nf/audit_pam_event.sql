-- audit_pam_event
-- Subtype for PAM event types:
--   CRED_ACQ, USER_ACCT, USER_START, USER_END, CRED_DISP, USER_AUTH, CRED_REFR
-- 3NF: single-column key (event_id); no other attributes.
-- Msg content lives in audit_message only.
-- Expected rows: 2,055 (1,525 intranet + 530 internal_share)

CREATE TABLE audit_pam_event (
    event_id  INTEGER  PRIMARY KEY REFERENCES audit_event(event_id)
);
