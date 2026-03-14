CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for openvpn.log source files.
-- This keeps the raw row shape from the findings docs plus provenance needed for traceability.
CREATE TABLE IF NOT EXISTS staging.river_vpn_events_staging (
    row_id          SERIAL PRIMARY KEY,
    source_host     VARCHAR(30) NOT NULL,
    source_log      VARCHAR(50) NOT NULL,
    line_number     INTEGER NOT NULL,
    raw_line        TEXT NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    client          VARCHAR(100) NOT NULL,
    message         TEXT NOT NULL,
    CONSTRAINT river_vpn_events_staging_line_number_ck CHECK (line_number > 0),
    CONSTRAINT river_vpn_events_staging_source_log_ck CHECK (source_log = 'openvpn.log'),
    CONSTRAINT river_vpn_events_staging_source_line_uq UNIQUE (source_host, source_log, line_number)
);

CREATE INDEX IF NOT EXISTS river_vpn_events_staging_event_ts_idx
    ON staging.river_vpn_events_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS river_vpn_events_staging_host_ts_idx
    ON staging.river_vpn_events_staging (source_host, event_timestamp);
