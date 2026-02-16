"""SQLAlchemy model package.

Import model modules here so they are registered on Base.metadata.
"""

from src.models.base import Base

__all__ = ["Base"]
