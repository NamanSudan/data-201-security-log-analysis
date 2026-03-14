CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for intranet_server/logs/apache2/intranet.smith.russellmitchell.com-error_log.2
-- Columns map to the tokens present in each raw log line plus line_number.
CREATE TABLE IF NOT EXISTS staging.ishaan_apache_error_staging (
    line_number     INTEGER                  PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    log_level       VARCHAR(50),
    client_ip       INET,
    message         TEXT                     NOT NULL,
    CONSTRAINT ishaan_apache_error_staging_line_number_ck CHECK (line_number > 0)
);

CREATE INDEX IF NOT EXISTS ishaan_apache_error_staging_event_ts_idx
    ON staging.ishaan_apache_error_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS ishaan_apache_error_staging_client_ip_ts_idx
    ON staging.ishaan_apache_error_staging (client_ip, event_timestamp);
