"""SQLAlchemy model for the auth log staging table."""

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class RiverAuthLogStaging(Base):
    """ORM mapping for `staging.river_auth_log_staging`."""

    __tablename__ = "river_auth_log_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="river_auth_log_staging_line_number_ck"),
        Index("river_auth_log_staging_event_ts_idx", "event_timestamp"),
        Index("river_auth_log_staging_host_ts_idx", "hostname", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_timestamp: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    process_name: Mapped[str] = mapped_column(String(50), nullable=False)
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
