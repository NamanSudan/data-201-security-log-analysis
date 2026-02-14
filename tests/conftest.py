"""Pytest configuration and fixtures."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def database_url():
    """Get the test database URL."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_password@localhost:5433/security_logs_test"
    )


@pytest.fixture(scope="session")
def engine(database_url):
    """Create a database engine for testing."""
    return create_engine(database_url)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
