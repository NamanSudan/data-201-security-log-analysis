-- stg_audit_line_raw: Shared table for audit.log lines (3,048 rows)
-- Sources: intranet_server (2,316) + internal_share (732)
-- msg column stores packed key-value blob as-is (1NF violation, deferred to 3NF)
-- Reference snapshot - canonical schema is in src/models/staging/audit.py

CREATE TABLE stg_audit_line_raw (
    row_id          SERIAL PRIMARY KEY,

    -- Provenance
    source_host     VARCHAR(30) NOT NULL,         -- YAML host_key, e.g. "intranet_server"
    source_log      VARCHAR(50) NOT NULL,         -- log filename, e.g. "audit.log"
    line_number     INTEGER NOT NULL,             -- 1-based line position in source file
    raw_line        TEXT NOT NULL,                -- full original line for auditability

    -- Audit header
    type            VARCHAR(20) NOT NULL,         -- event type, 15 distinct values
    epoch           DOUBLE PRECISION NOT NULL,    -- Unix timestamp with ms precision
    serial          INTEGER NOT NULL,             -- auditd serial number
    timestamp       TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Common fields
    pid             INTEGER,
    uid             INTEGER,
    auid            BIGINT,                       -- 4294967295 = unset sentinel
    ses             BIGINT,                       -- 4294967295 = unset sentinel

    -- msg blob (1NF violation -- contains op, acct, exe, hostname, addr, terminal, res, etc.)
    msg             TEXT,

    -- LOGIN-specific
    old_auid        BIGINT,
    old_ses         BIGINT,
    tty             VARCHAR(30),
    res             VARCHAR(10),                  -- LOGIN top-level result ("1" = success)

    -- AVC-specific
    apparmor        VARCHAR(20),
    operation       VARCHAR(30),
    info            TEXT,
    profile         VARCHAR(50),
    name            TEXT,

    -- SYSCALL / AVC shared
    comm            VARCHAR(50),

    -- SYSCALL-specific
    exe             TEXT,
    arch            VARCHAR(20),
    syscall         INTEGER,
    success         VARCHAR(5),
    exit            BIGINT,
    a0              VARCHAR(20),
    a1              VARCHAR(20),
    a2              VARCHAR(20),
    a3              VARCHAR(20),
    items           INTEGER,
    ppid            INTEGER,
    gid             INTEGER,
    euid            INTEGER,
    suid            INTEGER,
    fsuid           INTEGER,
    egid            INTEGER,
    sgid            INTEGER,
    fsgid           INTEGER,
    key             VARCHAR(20),

    -- PROCTITLE-specific
    proctitle       TEXT
);