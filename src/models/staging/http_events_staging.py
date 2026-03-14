"""SQLAlchemy model for the http error events staging table."""

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class IshaanApacheErrorStaging(Base):
    """ORM mapping for `staging.ishaan_apache_error_staging`."""

    __tablename__ = "ishaan_apache_error_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="ishaan_apache_error_staging_line_number_ck"),
        Index("ishaan_apache_error_staging_event_ts_idx", "event_timestamp"),
        Index("ishaan_apache_error_staging_client_ip_ts_idx", "client_ip", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_timestamp: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    log_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    client_ip: Mapped[str | None] = mapped_column(INET, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
