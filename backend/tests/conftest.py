"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.calculations import get_db
from app.db.base import Base
from app.main import app
from app.models import Calculation, Project, User
from engine.acoustic_engine import AcousticEngine
from engine.materials import Material


@pytest.fixture
def engine() -> AcousticEngine:
    """Return an acoustic engine instance."""
    return AcousticEngine()


@pytest.fixture
def material_test() -> Material:
    """Return a reusable concrete material."""
    return Material("Hormigon 200mm", densidad=2400, factor_pérdida=0.02)


@pytest.fixture
def db_session() -> Session:
    """Create an isolated SQLite database for API tests."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Return a FastAPI TestClient with the test database dependency."""
    _ = (Calculation, Project, User)

    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
