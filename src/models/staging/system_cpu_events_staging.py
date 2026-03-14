"""SQLAlchemy model for the system CPU events staging table."""

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class IshaanSystemCpuStaging(Base):
    """ORM mapping for `staging.ishaan_system_cpu_staging`."""

    __tablename__ = "ishaan_system_cpu_staging"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="ishaan_system_cpu_staging_line_number_ck"),
        Index("ishaan_system_cpu_staging_event_ts_idx", "event_timestamp"),
        Index("ishaan_system_cpu_staging_host_ts_idx", "hostname", "event_timestamp"),
        {"schema": "staging"},
    )

    line_number:     Mapped[int]            = mapped_column(Integer, primary_key=True)
    event_timestamp: Mapped[object | None]  = mapped_column(DateTime(timezone=True), nullable=True)
    hostname:        Mapped[str | None]     = mapped_column(String, nullable=True)
    cpu_total_pct:   Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_user_pct:    Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_system_pct:  Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_idle_pct:    Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_iowait_pct:  Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_steal_pct:   Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_softirq_pct: Mapped[float | None]   = mapped_column(Numeric(6, 4), nullable=True)
    cpu_cores:       Mapped[int | None]     = mapped_column(SmallInteger, nullable=True)
