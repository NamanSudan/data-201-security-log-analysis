"""3NF models for the host domain.

Tables:
  os_release       - OS release lookup (2 rows)
  host             - Central host reference (22 rows)
  host_group       - Group membership junction (63 rows)
  host_fqdn        - FQDN child table (20 rows)
  host_ipv4        - IPv4 address child table (24 rows)
  host_ipv6        - IPv6 address child table (24 rows)
  host_log_config  - Log configuration child table (66 rows)

Source: docs/schema/data_model_3nf.md (sections 2.1-2.7)
"""

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class OsRelease(Base):
    """3NF lookup table resolving distribution_release -> distribution, distribution_version."""

    __tablename__ = "os_release"

    os_release_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    distribution_release: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    distribution: Mapped[str] = mapped_column(String(50), nullable=False)
    distribution_version: Mapped[str] = mapped_column(String(20), nullable=False)


class Host(Base):
    """Central host reference entity. One row per testbed machine."""

    __tablename__ = "host"

    host_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hostname: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    openvpn_user: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_ipv4_address: Mapped[str] = mapped_column(String(45), nullable=False)
    default_ipv6_address: Mapped[str] = mapped_column(String(45), nullable=False)
    timezone: Mapped[str] = mapped_column(String(10), nullable=False)
    os_release_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("os_release.os_release_id"), nullable=False
    )


class HostGroup(Base):
    """1NF junction table for host <-> group membership (M:N, all-key)."""

    __tablename__ = "host_group"

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("host.host_id"), primary_key=True)
    group_name: Mapped[str] = mapped_column(String(50), primary_key=True)


class HostFqdn(Base):
    """1NF child table for host FQDNs (1:N, all-key)."""

    __tablename__ = "host_fqdn"

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("host.host_id"), primary_key=True)
    fqdn: Mapped[str] = mapped_column(String(255), primary_key=True)


class HostIpv4(Base):
    """1NF child table for host IPv4 addresses (1:N, all-key)."""

    __tablename__ = "host_ipv4"

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("host.host_id"), primary_key=True)
    ipv4_address: Mapped[str] = mapped_column(String(45), primary_key=True)


class HostIpv6(Base):
    """1NF child table for host IPv6 addresses (1:N, all-key)."""

    __tablename__ = "host_ipv6"

    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("host.host_id"), primary_key=True)
    ipv6_address: Mapped[str] = mapped_column(String(45), primary_key=True)


class HostLogConfig(Base):
    """Child table for per-host log collection configuration."""

    __tablename__ = "host_log_config"
    __table_args__ = (UniqueConstraint("host_id", "log_path", name="uq_host_log_config_host_path"),)

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("host.host_id"), nullable=False)
    log_path: Mapped[str] = mapped_column(Text, nullable=False)
    log_type: Mapped[str] = mapped_column(String(50), nullable=False)
    codec: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_chunk_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    add_field_json: Mapped[str | None] = mapped_column(Text, nullable=True)