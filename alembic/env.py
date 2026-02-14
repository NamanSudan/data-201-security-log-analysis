"""Alembic environment configuration.

This module configures Alembic to work with multiple environments (dev, test, prod)
by reading the APP_ENV environment variable and constructing the appropriate
database URL.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# from src.models import Base
# target_metadata = Base.metadata
target_metadata = None


def get_database_url() -> str:
    """
    Get the database URL based on the current environment.
    
    Priority:
    1. DATABASE_URL environment variable (for CI/CD)
    2. Constructed from individual env vars based on APP_ENV
    """
    # Check for explicit DATABASE_URL first (used in CI/CD)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Otherwise, construct from environment
    app_env = os.getenv("APP_ENV", "dev")
    
    if app_env == "test":
        return "postgresql://test_user:test_password@localhost:5433/security_logs_test"
    elif app_env == "prod":
        # Production should always use DATABASE_URL
        raise ValueError("Production environment requires DATABASE_URL to be set")
    else:  # dev
        user = os.getenv("DB_USER", "security_logs_user")
        password = os.getenv("DB_PASSWORD", "dev_password_change_me")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "security_logs")
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
