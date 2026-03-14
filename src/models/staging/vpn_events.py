"""SQLAlchemy model for the OpenVPN staging table."""

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class RiverVpnEventsStaging(Base):
    """ORM mapping for `staging.river_vpn_events_staging`."""

    __tablename__ = "river_vpn_events_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="river_vpn_events_staging_line_number_ck"),
        Index("river_vpn_events_staging_event_ts_idx", "event_timestamp"),
        Index("river_vpn_events_staging_host_ts_idx", "client", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_timestamp: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
