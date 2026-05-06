-- audit_service_event
-- Subtype for SERVICE_START, SERVICE_STOP.
-- Primary msg-derived attribute: unit (service name) - join audit_message on event_id.
-- 3NF: single-column key (event_id); no other attributes.
-- Expected rows: 555 (471 intranet + 84 internal_share)

CREATE TABLE audit_service_event (
    event_id  INTEGER  PRIMARY KEY REFERENCES audit_event(event_id)
);