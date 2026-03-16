"""3NF models for the audit domain.

Tables:
  audit_event            - Supertype; one row per raw audit log line (3,048 rows)
  audit_message          - Unpacked msg blob; 1NF resolution (0..1 per event, ~2,540 rows)
  audit_pam_event        - Subtype: PAM events (CRED_ACQ, USER_ACCT, USER_START, USER_END,
                           CRED_DISP, USER_AUTH, CRED_REFR) (~1,968 rows)
  audit_service_event    - Subtype: SERVICE_START, SERVICE_STOP (555 rows)
  audit_user_login_event - Subtype: USER_LOGIN (3 rows)
  audit_user_cmd_event   - Subtype: USER_CMD (1 row)
  audit_login_event      - Subtype: LOGIN (410 rows)
  audit_syscall_event    - Subtype: SYSCALL (8 rows)
  audit_avc_event        - Subtype: AVC (8 rows)
  audit_proctitle_event  - Subtype: PROCTITLE (8 rows)

Source: audit_3nf_normalization_plan.md (sections 6.1-6.3)
"""

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AuditEvent(Base):
    """Supertype table. One row per raw audit log line.

    Natural unique key: (host_id, line_number).
    3NF: PK = event_id; every non-key attribute depends only on event_id.
    host_id is an FK to the separate host entity (no transitive dependency).
    """

    __tablename__ = "audit_event"
    __table_args__ = (
        UniqueConstraint("host_id", "line_number", name="uq_audit_event_host_line"),
    )

    event_id:    Mapped[int]   = mapped_column(Integer,            primary_key=True, autoincrement=True)
    host_id:     Mapped[int]   = mapped_column(Integer,            ForeignKey("host.host_id"), nullable=False)
    line_number: Mapped[int]   = mapped_column(Integer,            nullable=False)
    raw_line:    Mapped[str]   = mapped_column(Text,               nullable=False)
    type:        Mapped[str]   = mapped_column(String(20),         nullable=False)
    epoch:       Mapped[float] = mapped_column(DOUBLE_PRECISION,   nullable=False)
    serial:      Mapped[int]   = mapped_column(Integer,            nullable=False)
    timestamp:   Mapped[str]   = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    pid:         Mapped[int | None]  = mapped_column(Integer,      nullable=True)
    uid:         Mapped[int | None]  = mapped_column(Integer,      nullable=True)
    auid:        Mapped[int | None]  = mapped_column(BigInteger,   nullable=True)  # 4294967295 = unset sentinel
    ses:         Mapped[int | None]  = mapped_column(BigInteger,   nullable=True)  # 4294967295 = unset sentinel


class AuditMessage(Base):
    """Unpacked msg blob; resolves 1NF violation in stg_audit_line_raw.

    Each of the 12 msg key-value pairs is stored as a separate atomic column.
    3NF: PK = event_id (FK to audit_event); every non-key attribute depends
    only on event_id. Cardinality: 0..1 per audit_event.
    """

    __tablename__ = "audit_message"

    event_id: Mapped[int]        = mapped_column(Integer,      ForeignKey("audit_event.event_id"), primary_key=True)
    op:       Mapped[str | None] = mapped_column(String(30),   nullable=True)
    acct:     Mapped[str | None] = mapped_column(String(50),   nullable=True)
    exe:      Mapped[str | None] = mapped_column(Text,         nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(50),   nullable=True)  # PAM/msg hostname, not host entity
    addr:     Mapped[str | None] = mapped_column(String(50),   nullable=True)
    terminal: Mapped[str | None] = mapped_column(String(30),   nullable=True)
    res:      Mapped[str | None] = mapped_column(String(20),   nullable=True)  # e.g. "success"
    unit:     Mapped[str | None] = mapped_column(String(100),  nullable=True)  # SERVICE_* events
    comm:     Mapped[str | None] = mapped_column(String(50),   nullable=True)
    id:       Mapped[int | None] = mapped_column(Integer,      nullable=True)  # USER_CMD
    cwd:      Mapped[str | None] = mapped_column(Text,         nullable=True)  # USER_CMD
    cmd:      Mapped[str | None] = mapped_column(Text,         nullable=True)  # USER_CMD (hex)


# ---------------------------------------------------------------------------
# Msg-bearing subtypes (event_id only; content lives in audit_message)
# ---------------------------------------------------------------------------

class AuditPamEvent(Base):
    """Subtype for PAM event types: CRED_ACQ, USER_ACCT, USER_START, USER_END,
    CRED_DISP, USER_AUTH, CRED_REFR.

    3NF: single-column key (event_id); no other attributes.
    Msg content lives in audit_message only.
    """

    __tablename__ = "audit_pam_event"

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("audit_event.event_id"), primary_key=True)


class AuditServiceEvent(Base):
    """Subtype for SERVICE_START, SERVICE_STOP.

    Primary msg-derived attribute: unit (service name) – join audit_message on event_id.
    3NF: single-column key (event_id); no other attributes.
    """

    __tablename__ = "audit_service_event"

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("audit_event.event_id"), primary_key=True)


class AuditUserLoginEvent(Base):
    """Subtype for USER_LOGIN.

    Primary msg-derived attribute: tty (terminal, e.g. ssh) – join audit_message on event_id.
    3NF: single-column key (event_id); no other attributes.
    """

    __tablename__ = "audit_user_login_event"

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("audit_event.event_id"), primary_key=True)


class AuditUserCmdEvent(Base):
    """Subtype for USER_CMD.

    Msg-derived attributes: cmd, cwd, id – join audit_message on event_id.
    3NF: single-column key (event_id); no other attributes.
    """

    __tablename__ = "audit_user_cmd_event"

    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("audit_event.event_id"), primary_key=True)


# ---------------------------------------------------------------------------
# Outer-field subtypes (non-key columns sourced from staging outer fields)
# ---------------------------------------------------------------------------

class AuditLoginEvent(Base):
    """Subtype for LOGIN events.

    3NF: PK = event_id; every non-key (old_auid, old_ses, tty, res)
    depends only on event_id. No partial or transitive dependency.
    """

    __tablename__ = "audit_login_event"

    event_id: Mapped[int]        = mapped_column(Integer,     ForeignKey("audit_event.event_id"), primary_key=True)
    old_auid: Mapped[int | None] = mapped_column(BigInteger,  nullable=True)  # often 4294967295 sentinel
    old_ses:  Mapped[int | None] = mapped_column(BigInteger,  nullable=True)  # often 4294967295 sentinel
    tty:      Mapped[str | None] = mapped_column(String(30),  nullable=True)  # e.g. "(none)"
    res:      Mapped[str | None] = mapped_column(String(10),  nullable=True)  # e.g. "1" (success)


class AuditSyscallEvent(Base):
    """Subtype for SYSCALL events.

    3NF: PK = event_id; all non-key columns depend only on event_id.
    Note: low-value columns a0-a3, items, ppid, gid, euid, suid, fsuid,
    egid, sgid, fsgid omitted pending open decision (plan §10.3).
    """

    __tablename__ = "audit_syscall_event"

    event_id: Mapped[int]        = mapped_column(Integer,    ForeignKey("audit_event.event_id"), primary_key=True)
    arch:     Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g. x86_64
    syscall:  Mapped[int | None] = mapped_column(Integer,    nullable=True)  # syscall number
    success:  Mapped[str | None] = mapped_column(String(5),  nullable=True)  # yes / no
    exit:     Mapped[int | None] = mapped_column(BigInteger,  nullable=True)  # exit code
    exe:      Mapped[str | None] = mapped_column(Text,        nullable=True)  # executable path
    comm:     Mapped[str | None] = mapped_column(String(50), nullable=True)  # command name
    key:      Mapped[str | None] = mapped_column(String(20), nullable=True)  # audit key


class AuditAvcEvent(Base):
    """Subtype for AVC events.

    3NF: PK = event_id; every non-key attribute depends only on event_id.
    No partial or transitive dependency.
    """

    __tablename__ = "audit_avc_event"

    event_id:  Mapped[int]        = mapped_column(Integer,    ForeignKey("audit_event.event_id"), primary_key=True)
    apparmor:  Mapped[str | None] = mapped_column(String(20), nullable=True)  # AppArmor subsystem
    operation: Mapped[str | None] = mapped_column(String(30), nullable=True)  # e.g. profile_replace
    profile:   Mapped[str | None] = mapped_column(String(50), nullable=True)
    name:      Mapped[str | None] = mapped_column(Text,       nullable=True)  # resource name
    info:      Mapped[str | None] = mapped_column(Text,       nullable=True)  # additional info
    comm:      Mapped[str | None] = mapped_column(String(50), nullable=True)


class AuditProctitleEvent(Base):
    """Subtype for PROCTITLE events.

    3NF: PK = event_id; single non-key (proctitle) depends only on event_id.
    """

    __tablename__ = "audit_proctitle_event"

    event_id:  Mapped[int]        = mapped_column(Integer, ForeignKey("audit_event.event_id"), primary_key=True)
    proctitle: Mapped[str | None] = mapped_column(Text,    nullable=True)  # hex-encoded command line
