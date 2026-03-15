-- stg_http_access: Raw 1:1 with Apache Combined Log Format lines
-- Source: intranet_smith_russellmitchell_com-access_log.2
-- Notebook: 03_explore_httpsaccess_log_intranet.ipynb
-- Candidate key: (source_host, source_log, line_number)

CREATE TABLE stg_http_access (
    row_id              SERIAL PRIMARY KEY,
    source_host         VARCHAR(30)     NOT NULL,           -- YAML host_key, e.g. "intranet-server"
    source_log          VARCHAR(100)    NOT NULL,           -- log filename, e.g. "intranet_smith_russellmitchell_com-access_log.2"
    line_number         INTEGER         NOT NULL,           -- 1-based line number in the raw log file
    timestamp           TIMESTAMPTZ,                        -- parsed UTC timestamp
    raw_timestamp       VARCHAR(30),                        -- original CLF string, e.g. "24/Jan/2022:03:57:26 +0000"
    client_ip           INET            NOT NULL,           -- requesting client IP, e.g. "172.19.131.174"
    ident               VARCHAR(255),                       -- RFC 1413 ident (almost always NULL / "-")
    authuser            VARCHAR(255),                       -- HTTP authenticated user (NULL if "-")
    http_method         VARCHAR(10),                        -- HTTP verb, e.g. "GET", "POST", "HEAD"
    path                TEXT,                               -- URL path component, e.g. "/wp-login.php"
    query_string        TEXT,                               -- raw query string (NULL if none)
    http_proto          VARCHAR(10),                        -- protocol version, e.g. "HTTP/1.1"
    status              SMALLINT        NOT NULL,           -- HTTP response status code, e.g. 200, 404
    bytes_sent          BIGINT,                             -- response body bytes (NULL if "-")
    referer             TEXT,                               -- HTTP Referer header (NULL if "-")
    user_agent          TEXT,                               -- HTTP User-Agent string (NULL if "-")
    request_line        TEXT                                -- full raw request line, e.g. "GET /wp-login.php HTTP/1.1"
);
