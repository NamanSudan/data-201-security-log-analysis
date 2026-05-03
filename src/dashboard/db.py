"""Database helpers for the Streamlit dashboard.

Mirrors the loader pattern in src/loaders/load_3nf.py: read DATABASE_URL
or DB_* environment variables, build a SQLAlchemy engine, and run SQL
strings or files into pandas DataFrames.

The engine is cached for the lifetime of the Python process via
functools.lru_cache so repeated Streamlit reruns reuse the same pool
instead of spawning a new connection per chart.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text

# Repo root is two levels above this file: src/dashboard/db.py -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]


def _build_database_url() -> str:
    """Build the SQLAlchemy URL from environment.

    Loads the repo-root .env file if present, then prefers an explicit
    DATABASE_URL, falling back to assembling one from DB_* variables.
    Defaults match docker-compose.yml so the dashboard can boot against
    the development DB without a populated .env.
    """
    load_dotenv(REPO_ROOT / ".env")
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    user = os.getenv("DB_USER", "security_logs_user")
    password = os.getenv("DB_PASSWORD", "dev_password_change_me")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "security_logs")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine.

    pool_pre_ping keeps stale connections from leaking into the
    Streamlit reruns (Docker restarts, laptop sleep, etc.).
    """
    return create_engine(_build_database_url(), pool_pre_ping=True)


def run_sql(engine: Engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a SQL string and return the result as a DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def run_sql_file(
    engine: Engine,
    sql_path: str | Path,
    params: dict | None = None,
) -> pd.DataFrame:
    """Load a .sql file from disk and execute it.

    sql_path is resolved relative to the repo root if it is not
    already absolute. Comments and blank lines are passed through to
    psycopg2 unchanged.
    """
    path = Path(sql_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    sql = path.read_text(encoding="utf-8")
    return run_sql(engine, sql, params=params)
