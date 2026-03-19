"""SQLAlchemy model package.

Import model modules here so they are registered on Base.metadata.
"""

from src.models.base import Base
from src.models.final import (
    Host,
    HostFqdn,
    HostGroup,
    HostIpv4,
    HostIpv6,
    HostLogConfig,
    OsRelease,
)
from src.models.staging import (
    StgAttackLabelLineRaw,
    StgAuditLineRaw,
    StgHostLogConfigRaw,
    StgHostRaw,
)

__all__ = [
    "Base",
    # Staging
    "StgHostRaw",
    "StgHostLogConfigRaw",
    "StgAuditLineRaw",
    "StgAttackLabelLineRaw",
    # 3NF host domain
    "OsRelease",
    "Host",
    "HostGroup",
    "HostFqdn",
    "HostIpv4",
    "HostIpv6",
    "HostLogConfig",
]