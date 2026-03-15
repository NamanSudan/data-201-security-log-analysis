-- stg_http_errors: Raw 1:1 with Apache error log lines
-- Source: intranet_smith_russellmitchell_com-error_log.2
-- Notebook: 02_explore_httpserror_log_intranet.ipynb
-- Candidate key: (source_host, source_log, line_number)

CREATE TABLE stg_http_errors (
    row_id              SERIAL PRIMARY KEY,
    source_host         VARCHAR(30)     NOT NULL,           -- YAML host_key, e.g. "intranet-server"
    source_log          VARCHAR(100)    NOT NULL,           -- log filename, e.g. "intranet_smith_russellmitchell_com-error_log.2"
    line_number         INTEGER         NOT NULL,           -- 1-based line number in the raw log file
    timestamp           TIMESTAMPTZ,                        -- parsed UTC timestamp
    raw_timestamp       VARCHAR(40),                        -- original string, e.g. "Mon Jan 24 03:57:26.696483 2022"
    module              VARCHAR(20)     NOT NULL,           -- Apache module, e.g. "authz_core", "php7"
    level               VARCHAR(10)     NOT NULL,           -- log level, e.g. "error", "notice"
    pid                 INTEGER,                            -- Apache worker process ID
    client_ip           INET,                               -- client IP address (NULL if not present)
    client_port         INTEGER,                            -- client port (NULL if not present)
    error_code          VARCHAR(10),                        -- AH##### code, e.g. "AH01630" (NULL if absent)
    message             TEXT,                               -- cleaned message body (AH code prefix stripped)
    message_raw         TEXT,                               -- full original message field
    target_path         TEXT,                               -- extracted file/directory path (NULL if absent)
    referer             TEXT                                -- HTTP Referer from log line (NULL if absent)
);
