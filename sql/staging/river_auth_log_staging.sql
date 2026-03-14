CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for intranet_server/logs/auth.log.
-- Columns map to the tokens present in each raw log line plus line_number.
CREATE TABLE IF NOT EXISTS staging.river_auth_log_staging (
    line_number     INTEGER PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    hostname        VARCHAR(100),
    process_name    VARCHAR(50) NOT NULL,
    pid             INTEGER,
    message         TEXT NOT NULL,
    CONSTRAINT river_auth_log_staging_line_number_ck CHECK (line_number > 0)
);

CREATE INDEX IF NOT EXISTS river_auth_log_staging_event_ts_idx
    ON staging.river_auth_log_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS river_auth_log_staging_host_ts_idx
    ON staging.river_auth_log_staging (hostname, event_timestamp);
