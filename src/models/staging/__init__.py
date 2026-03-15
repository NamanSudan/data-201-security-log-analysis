"""Staging table ORM models.

Import all staging models here so Alembic autogenerate picks them up.
"""

from src.models.staging.audit import StgAuditLineRaw
from src.models.staging.host import StgHostLogConfigRaw, StgHostRaw
from src.models.staging.labels import StgAttackLabelLineRaw
from src.models.staging.http_apache_error import StgHttpErrors
from src.models.staging.http_apache_access import StgHttpAccess
from src.models.staging.system_cpu_internal import StgSystemCpuEvents

__all__ = [
    "StgHostRaw",
    "StgHostLogConfigRaw",
    "StgAuditLineRaw",
    "StgAttackLabelLineRaw",
    "StgHttpErrors",
    "StgHttpAccess",
    "StgSystemCpuEvents",
]
