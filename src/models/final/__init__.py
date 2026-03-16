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
from src.models.final.labels import (
    AttackLabel,
    AttackPhase,
    LabeledLine,
    LabeledLineLabel,
    LabeledLineRule,
)

__all__ = [
    "OsRelease",
    "Host",
    "HostGroup",
    "HostFqdn",
    "HostIpv4",
    "HostIpv6",
    "HostLogConfig",
    "AttackPhase",
    "AttackLabel",
    "LabeledLine",
    "LabeledLineLabel",
    "LabeledLineRule",
]
