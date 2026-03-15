"""Staging model for Apache HTTP error log lines.

Table:
    stg_http_errors - raw 1:1 with parsed Apache error log lines

Source: intranet_smith_russellmitchell_com-error_log.2
Notebook: 02_explore_httpserror_log_intranet.ipynb

Candidate key: (source_host, source_log, line_number)
"""

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgHttpErrors(Base):
    __tablename__ = "stg_http_errors"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(100), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_timestamp: Mapped[str] = mapped_column(String(40), nullable=True)
    module: Mapped[str] = mapped_column(String(20), nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    pid: Mapped[int] = mapped_column(Integer, nullable=True)
    client_ip: Mapped[str] = mapped_column(INET, nullable=True)
    client_port: Mapped[int] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str] = mapped_column(String(10), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    message_raw: Mapped[str] = mapped_column(Text, nullable=True)
    target_path: Mapped[str] = mapped_column(Text, nullable=True)
    referer: Mapped[str] = mapped_column(Text, nullable=True)
