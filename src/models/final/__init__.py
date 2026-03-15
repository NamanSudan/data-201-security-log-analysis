"""3NF final table ORM models.

Import all final models here so Alembic autogenerate picks them up.
"""

from src.models.final.host import (
    Host,
    HostFqdn,
    HostGroup,
    HostIpv4,
    HostIpv6,
    HostLogConfig,
    OsRelease,
)

__all__ = [
    "OsRelease",
    "Host",
    "HostGroup",
    "HostFqdn",
    "HostIpv4",
    "HostIpv6",
    "HostLogConfig",
]
