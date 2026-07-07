"""Shared fixtures for all tests."""

import json
from datetime import datetime, timezone
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.auth.security import hash_password
from backend.db.database import Base, get_db
from backend.db.models import Alert, Summary, User


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="db_session")
def db_session_fixture() -> Generator[Session, None, None]:
    """In-memory SQLite session — fresh tables per test.

    Uses StaticPool so all connections share the same :memory: database.
    Without this, create_all() and the session would get different DBs.
    """
    # Use an in-memory engine for tests and ensure the project's
    # backend.db.database.SessionLocal/engine point to it so all code
    # (including scrapers) uses the same test DB.
    import backend.db.database as _db

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Patch the backend database module to use our test engine/session
    _db.engine = engine
    _db.SessionLocal = sessionmaker(bind=engine)

    # Also ensure the top-level db.database module used across the project
    # points to the same engine/session so all imports share the test DB.
    import importlib
    try:
        _top = importlib.import_module("db.database")
        _top.engine = engine
        _top.SessionLocal = _db.SessionLocal
        _top.Base = _db.Base
    except Exception:
        # If top-level db package is not yet imported, ignore — imports will
        # reference backend.db.database directly in that case.
        pass

    Base.metadata.create_all(bind=engine)
    # Ensure top-level db.database Base metadata is synced so imported models
    # (which reference db.database.Base) have tables created in this in-memory DB.
    try:
        import db.database as _topdb
        _topdb.Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    session_factory = _db.SessionLocal
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the in-memory DB.

    Creates a fresh app without lifespan (no scheduler, no prod DB init)
    so tests run isolated and fast.
    """
    from fastapi.middleware.cors import CORSMiddleware
    from backend.api.router import api_router

    test_app = FastAPI(title="RiskRadar API Test")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(api_router)
    test_app.add_api_route(
        "/",
        lambda: {"name": "RiskRadar API", "version": "1.0.0", "status": "running"},
    )

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    test_app.dependency_overrides[get_db] = _override_get_db
    client = TestClient(test_app)
    yield client
    test_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

NOW = datetime.now(timezone.utc)


@pytest.fixture(name="sample_alerts")
def sample_alerts_fixture(db_session: Session) -> list[Alert]:
    """Insert 3 alerts of different types."""
    alerts = [
        Alert(
            source="nws",
            source_id="nws_001",
            alert_type="weather",
            severity="high",
            title="Severe Thunderstorm Warning",
            description="Strong storms expected in the area.",
            latitude=34.05,
            longitude=-118.24,
            location_name="Los Angeles, CA",
            event_start=NOW,
            event_end=NOW,
            fetched_at=NOW,
            created_at=NOW,
            updated_at=NOW,
        ),
        Alert(
            source="epa",
            source_id="epa_001",
            alert_type="pollution",
            severity="moderate",
            title="TRI Facility: Test Chemical Co",
            description="Toxic release inventory facility.",
            latitude=34.10,
            longitude=-118.30,
            location_name="Pasadena, CA",
            fetched_at=NOW,
            created_at=NOW,
            updated_at=NOW,
        ),
        Alert(
            source="usgs_earthquakes",
            source_id="usgs_001",
            alert_type="earthquake",
            severity="low",
            title="M 2.8 - 10km NW of Los Angeles",
            description="Minor earthquake detected.",
            latitude=34.15,
            longitude=-118.40,
            location_name="10km NW of Los Angeles",
            event_start=NOW,
            fetched_at=NOW,
            created_at=NOW,
            updated_at=NOW,
        ),
    ]
    db_session.add_all(alerts)
    db_session.commit()
    for alert in alerts:
        db_session.refresh(alert)
    return alerts


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Insert a test user."""
    user = User(
        display_name="Test User",
        email="test@example.com",
        password_hash=hash_password("password123"),
        zip_code="90001",
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_summary(db_session: Session, request: pytest.FixtureRequest) -> Summary:
    """Insert a test summary."""
    sample_alerts = request.getfixturevalue("sample_alerts")
    summary = Summary(
        title="Environmental Digest — Mar 02, 2026",
        content="## Executive Summary\nMultiple alerts detected.",
        summary_type="daily",
        alert_ids=json.dumps([alert.id for alert in sample_alerts]),
        region="US",
        generated_at=NOW,
        model_used="gpt-4o-mini",
        token_count=150,
        created_at=NOW,
    )
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    return summary
