CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for vpn/logs/openvpn.log.
-- Columns map to the tokens present in each raw log line plus line_number.
CREATE TABLE IF NOT EXISTS staging.river_vpn_events_staging (
    line_number     INTEGER PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    client          VARCHAR(100) NOT NULL,
    message         TEXT NOT NULL,
    CONSTRAINT river_vpn_events_staging_line_number_ck CHECK (line_number > 0)
);

CREATE INDEX IF NOT EXISTS river_vpn_events_staging_event_ts_idx
    ON staging.river_vpn_events_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS river_vpn_events_staging_host_ts_idx
    ON staging.river_vpn_events_staging (client, event_timestamp);
