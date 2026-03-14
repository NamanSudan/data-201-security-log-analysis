-- =============================================================================
-- Raw (Unnormalized, Lossless) DDL: Apache Error Log → http_events
-- Source : russellmitchell/gather/intranet_server/logs/apache2/
--          intranet.smith.russellmitchell.com-error_log.2
-- Labels : russellmitchell/labels/intranet_server/logs/apache2/
--          intranet.smith.russellmitchell.com-error_log.2
-- Rows   : 35  |  Columns: 12
-- =============================================================================

CREATE TABLE http_events (
    http_event_id          SERIAL          PRIMARY KEY,
    event_id               INTEGER         NOT NULL,
    event_timestamp        TIMESTAMP,
    log_level              VARCHAR(50),
    pid                    INTEGER,
    client_ip              INET,
    client_port            INTEGER,
    message                TEXT,
    referer                TEXT,
    http_event_category    TEXT[],
    http_signature_matches JSONB,
    created_at             TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
