-- =============================================================================
-- Raw (Unnormalized) DDL: Apache Access Log → http_access_events
-- Source : russellmitchell/gather/intranet_server/logs/apache2/
--          intranet.smith.russellmitchell.com-access_log.2
-- Labels : russellmitchell/labels/intranet_server/logs/apache2/
--          intranet.smith.russellmitchell.com-access_log.2
-- Rows   : 7695  |  Columns: 16
-- =============================================================================

CREATE TABLE http_access_events (
    http_access_event_id          SERIAL                   PRIMARY KEY,
    event_id                      INTEGER                  NOT NULL,
    event_timestamp               TIMESTAMP WITH TIME ZONE,
    client_ip                     INET,
    http_method                   VARCHAR(10),
    request_url                   TEXT,
    url_path                      TEXT,
    query_string                  TEXT,
    protocol                      VARCHAR(10),
    status_code                   SMALLINT,
    bytes_sent                    INTEGER,
    referer                       TEXT,
    decoded_command               TEXT,
    request_type                  VARCHAR(20),
    http_access_event_category    TEXT[],
    http_access_signature_matches JSONB,
    created_at                    TIMESTAMP                DEFAULT CURRENT_TIMESTAMP
);
