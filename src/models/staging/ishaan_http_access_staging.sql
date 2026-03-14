CREATE SCHEMA IF NOT EXISTS staging;

-- 1:1 staging table for intranet_server/logs/apache2/
-- intranet.smith.russellmitchell.com-access_log.2
-- Columns map to the tokens present in each raw log line plus line_number.
CREATE TABLE IF NOT EXISTS staging.ishaan_http_access_staging (
    line_number    INTEGER PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE,
    client_ip      INET,
    http_method    VARCHAR(10),
    request_url    TEXT,
    url_path       TEXT,
    query_string   TEXT,
    status_code    SMALLINT,
    bytes_sent     INTEGER,
    CONSTRAINT ishaan_http_access_staging_line_number_ck CHECK (line_number > 0)
);

CREATE INDEX IF NOT EXISTS ishaan_http_access_staging_event_ts_idx
    ON staging.ishaan_http_access_staging (event_timestamp);

CREATE INDEX IF NOT EXISTS ishaan_http_access_staging_client_ip_ts_idx
    ON staging.ishaan_http_access_staging (client_ip, event_timestamp);
