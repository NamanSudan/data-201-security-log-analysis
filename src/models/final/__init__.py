"""3NF final table ORM models.

Import all final models here so Alembic autogenerate picks them up.
"""

from src.models.final.audit import (
    AuditAvcEvent,
    AuditEvent,
    AuditLoginEvent,
    AuditMessage,
    AuditPamEvent,
    AuditProctitleEvent,
    AuditServiceEvent,
    AuditSyscallEvent,
    AuditUserCmdEvent,
    AuditUserLoginEvent,
)
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
    # Host domain
    "OsRelease",
    "Host",
    "HostGroup",
    "HostFqdn",
    "HostIpv4",
    "HostIpv6",
    "HostLogConfig",
    # Labels domain
    "AttackPhase",
    "AttackLabel",
    "LabeledLine",
    "LabeledLineLabel",
    "LabeledLineRule",
    # Audit domain
    "AuditEvent",
    "AuditMessage",
    "AuditPamEvent",
    "AuditServiceEvent",
    "AuditUserLoginEvent",
    "AuditUserCmdEvent",
    "AuditLoginEvent",
    "AuditSyscallEvent",
    "AuditAvcEvent",
    "AuditProctitleEvent",
]
