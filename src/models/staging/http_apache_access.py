"""Staging model for Apache HTTP access log lines.

Table:
    stg_http_access - raw 1:1 with Apache Combined Log Format lines

Source: intranet_smith_russellmitchell_com-access_log.2
Notebook: 03_explore_httpsaccess_log_intranet.ipynb

Candidate key: (source_host, source_log, line_number)
"""

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgHttpAccess(Base):
    __tablename__ = "stg_http_access"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(100), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_timestamp: Mapped[str] = mapped_column(String(30), nullable=True)
    client_ip: Mapped[str] = mapped_column(INET, nullable=False)
    ident: Mapped[str] = mapped_column(String(255), nullable=True)
    authuser: Mapped[str] = mapped_column(String(255), nullable=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=True)
    query_string: Mapped[str] = mapped_column(Text, nullable=True)
    http_proto: Mapped[str] = mapped_column(String(10), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    bytes_sent: Mapped[int] = mapped_column(BigInteger, nullable=True)
    referer: Mapped[str] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    request_line: Mapped[str] = mapped_column(Text, nullable=True)
