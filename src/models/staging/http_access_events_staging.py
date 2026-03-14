"""SQLAlchemy model for the http access events staging table."""

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class IshaanApacheAccessStaging(Base):
    """ORM mapping for `staging.ishaan_apache_access_staging`."""

    __tablename__ = "ishaan_apache_access_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="ishaan_apache_access_staging_line_number_ck"),
        Index("ishaan_apache_access_staging_event_ts_idx", "event_timestamp"),
        Index("ishaan_apache_access_staging_client_ip_ts_idx", "client_ip", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number:     Mapped[int]              = mapped_column(Integer, primary_key=True)
    event_timestamp: Mapped[object | None]   = mapped_column(DateTime(timezone=True), nullable=True)
    client_ip:       Mapped[str | None]      = mapped_column(INET, nullable=True)
    http_method:     Mapped[str | None]      = mapped_column(String(10), nullable=True)
    request_url:     Mapped[str | None]      = mapped_column(Text, nullable=True)
    protocol:        Mapped[str | None]      = mapped_column(String(10), nullable=True)
    status_code:     Mapped[int | None]      = mapped_column(SmallInteger, nullable=True)
    bytes_sent:      Mapped[int | None]      = mapped_column(Integer, nullable=True)
    referer:         Mapped[str | None]      = mapped_column(Text, nullable=True)
