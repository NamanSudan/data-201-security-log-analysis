-- audit_syscall_event
-- Subtype for SYSCALL events.
-- 3NF: PK = event_id; all non-key columns depend only on event_id.
-- tty: top-level auditd field (e.g. "pts1", "pts0"); all 8 rows non-null (validated).
--      Distinct from msg-embedded terminal in audit_message.
-- Note: low-value columns a0-a3, items, ppid, gid, euid, suid, fsuid,
-- egid, sgid, fsgid omitted pending open decision (plan §10.3).
-- Expected rows: 8 (4 intranet + 4 internal_share)

CREATE TABLE audit_syscall_event (
    event_id  INTEGER      PRIMARY KEY REFERENCES audit_event(event_id),
    arch      VARCHAR(20), -- e.g. x86_64
    syscall   INTEGER,     -- syscall number
    success   VARCHAR(5),  -- yes / no
    exit      BIGINT,      -- exit code
    exe       TEXT,        -- executable path
    comm      VARCHAR(50), -- command name
    tty       VARCHAR(30), -- top-level auditd field (e.g. "pts1", "pts0")
    key       VARCHAR(20)  -- audit key
);
