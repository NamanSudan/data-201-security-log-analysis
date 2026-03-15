"""Staging model for Metricbeat system/cpu metric records.

Table:
    stg_system_cpu_events - raw 1:1 with Metricbeat system/cpu JSON records

Source: 2022-01-21-system_cpu.log (internal_share)
Notebook: 08_system_cpu_internal_share.ipynb

Candidate key: (source_host, source_log, event_timestamp)
"""

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgSystemCpuEvents(Base):
    __tablename__ = "stg_system_cpu_events"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_host: Mapped[str] = mapped_column(String(30), nullable=False)
    source_log: Mapped[str] = mapped_column(String(100), nullable=False)
    event_timestamp: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=True)
    cpu_total_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_user_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_system_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_idle_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_iowait_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_steal_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_softirq_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_irq_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_nice_pct: Mapped[float] = mapped_column(Numeric(6, 4), nullable=True)
    cpu_cores: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    event_duration_ns: Mapped[int] = mapped_column(BigInteger, nullable=True)
    metricset_period_ms: Mapped[int] = mapped_column(Integer, nullable=True)
