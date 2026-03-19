"""Staging models for host inventory (servers.yaml).

Tables:
  stg_host_raw           - one row per host (22 rows)
  stg_host_log_config_raw - one row per log config entry (66 rows)

Multi-valued fields (groups, fqdns, ipv4_addresses, ipv6_addresses) are stored
as JSON-array strings in TEXT columns. Parsing is deferred to 3NF ETL.
"""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class StgHostRaw(Base):
    __tablename__ = "stg_host_raw"

    host_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hostname: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    groups: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    openvpn_user: Mapped[str | None] = mapped_column(String(50), nullable=True)
    distribution: Mapped[str] = mapped_column(String(50), nullable=False)
    distribution_release: Mapped[str] = mapped_column(String(20), nullable=False)
    distribution_version: Mapped[str] = mapped_column(String(20), nullable=False)
    default_ipv4_address: Mapped[str] = mapped_column(String(45), nullable=False)
    default_ipv6_address: Mapped[str] = mapped_column(String(45), nullable=False)
    ipv4_addresses: Mapped[str] = mapped_column(Text, nullable=False)
    ipv6_addresses: Mapped[str] = mapped_column(Text, nullable=False)
    fqdns: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(10), nullable=False)


class StgHostLogConfigRaw(Base):
    __tablename__ = "stg_host_log_config_raw"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stg_host_raw.host_id"), nullable=False
    )
    log_path: Mapped[str] = mapped_column(Text, nullable=False)
    log_type: Mapped[str] = mapped_column(String(50), nullable=False)
    codec: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_chunk_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    add_field_json: Mapped[str | None] = mapped_column(Text, nullable=True)
