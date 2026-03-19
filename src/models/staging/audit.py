"""Staging model for audit log lines.

Table:
  stg_audit_line_raw - shared table for both audit.log sources (3,048 rows)
                       intranet_server (2,316) + internal_share (732)

The msg column stores the full msg='...' string as a TEXT blob.
Unpacking to 3NF subtypes is deferred to iteration 2.
"""

from sqlalchemy import BigInteger, Double, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgAuditLineRaw(Base):
    __tablename__ = "stg_audit_line_raw"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Provenance
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(50), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_line: Mapped[str] = mapped_column(Text, nullable=False)

    # Audit header
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    epoch: Mapped[float] = mapped_column(Double, nullable=False)
    serial: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Common fields
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    auid: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ses: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # msg blob (1NF violation, deferred)
    msg: Mapped[str | None] = mapped_column(Text, nullable=True)

    # LOGIN-specific
    old_auid: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    old_ses: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tty: Mapped[str | None] = mapped_column(String(30), nullable=True)
    res: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # AVC-specific
    apparmor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    operation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    info: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)

    # SYSCALL / AVC shared
    comm: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # SYSCALL-specific
    exe: Mapped[str | None] = mapped_column(Text, nullable=True)
    arch: Mapped[str | None] = mapped_column(String(20), nullable=True)
    syscall: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[str | None] = mapped_column(String(5), nullable=True)
    exit: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    a0: Mapped[str | None] = mapped_column(String(20), nullable=True)
    a1: Mapped[str | None] = mapped_column(String(20), nullable=True)
    a2: Mapped[str | None] = mapped_column(String(20), nullable=True)
    a3: Mapped[str | None] = mapped_column(String(20), nullable=True)
    items: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ppid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    euid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fsuid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    egid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sgid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fsgid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    key: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # PROCTITLE-specific
    proctitle: Mapped[str | None] = mapped_column(Text, nullable=True)
