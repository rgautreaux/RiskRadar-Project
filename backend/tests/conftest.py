"""Shared fixtures for all tests."""

import json
import pytest
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient

from db.database import Base, get_db
from db.models import Alert, Summary, User, ScrapeLog


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session():
    """In-memory SQLite session — fresh tables per test.

    Uses StaticPool so all connections share the same :memory: database.
    Without this, create_all() and the session would get different DBs.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(db_session):
    """FastAPI TestClient wired to the in-memory DB.

    Creates a fresh app without lifespan (no scheduler, no prod DB init)
    so tests run isolated and fast.
    """
    from fastapi.middleware.cors import CORSMiddleware
    from api.router import api_router

    # Build a clean app without the lifespan that starts the scheduler
    test_app = FastAPI(title="RiskRadar API Test")
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    test_app.include_router(api_router)

    # Wire the root endpoint
    @test_app.get("/")
    def root():
        return {"name": "RiskRadar API", "version": "1.0.0", "status": "running"}

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


@pytest.fixture
def sample_alerts(db_session):
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
    for a in alerts:
        db_session.refresh(a)
    return alerts


@pytest.fixture
def sample_user(db_session):
    """Insert a test user."""
    import hashlib

    user = User(
        display_name="Test User",
        email="test@example.com",
        password_hash=hashlib.sha256("password123".encode()).hexdigest(),
        zip_code="90001",
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_summary(db_session, sample_alerts):
    """Insert a test summary."""
    summary = Summary(
        title="Environmental Digest — Mar 02, 2026",
        content="## Executive Summary\nMultiple alerts detected.",
        summary_type="daily",
        alert_ids=json.dumps([a.id for a in sample_alerts]),
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
