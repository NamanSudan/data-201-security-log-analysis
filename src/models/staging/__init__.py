"""Staging ORM models for Alembic metadata registration."""

from src.models.staging.http_access_events_staging import IshaanApacheAccessStaging
from src.models.staging.http_events_staging import IshaanApacheErrorStaging
from src.models.staging.system_cpu_events_staging import IshaanSystemCpuStaging

__all__ = [
    "IshaanApacheAccessStaging",
    "IshaanApacheErrorStaging",
    "IshaanSystemCpuStaging",
]
