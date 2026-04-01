"""Live data-fetch tests for all scrapers and internal API endpoints.

Purpose
-------
Validates that every scraper and API can successfully reach its data source
and return raw records.  Results are printed for every test:

  PASS — shows the number of items fetched
  FAIL — shows the full error so you know exactly what went wrong

Usage
-----
Run all live tests (hits real external APIs):

    pytest tests/test_live_data_fetch.py -v -s

Run only the internal API endpoint tests (no external calls):

    pytest tests/test_live_data_fetch.py -v -s -m "not live"

Run only the live scraper tests:

    pytest tests/test_live_data_fetch.py -v -s -m live

Notes
-----
- Scrapers that require an API key are automatically skipped when the
  corresponding environment variable is not configured.
- Internal API endpoint tests use an in-memory SQLite database so they
  never touch the production database.
"""

import os
import pytest
import yaml
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from config.settings import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_env(var_name: str, label: str) -> None:
    """Skip the calling test if *var_name* is not set in the environment."""
    value = os.environ.get(var_name, "").strip() or str(getattr(settings, var_name, "")).strip()
    if not value:
        pytest.skip(f"{label} — {var_name} not configured, skipping live test")


def _load_source_config(name: str) -> dict:
    """Return the api_source entry for *name* from sources.yaml."""
    config_path = Path(settings.SOURCES_CONFIG_PATH)
    with open(config_path) as fh:
        cfg = yaml.safe_load(fh)
    for source in cfg.get("api_sources", []):
        if source.get("name") == name:
            return source
    raise KeyError(f"Source '{name}' not found in sources.yaml")


# ---------------------------------------------------------------------------
# Shared fixture: FastAPI TestClient backed by in-memory SQLite
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def api_client():
    """Return a TestClient wired to an isolated in-memory database.

    Uses module scope so the database is created once for all API endpoint
    tests in this file, keeping the suite fast.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    from api.router import api_router

    app = FastAPI(title="RiskRadar — Live Test Client")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    def _root():
        return {"name": "RiskRadar API", "version": "1.0.0", "status": "running"}

    def _override_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_db
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


# ===========================================================================
# SCRAPER LIVE TESTS
# Each class tests one scraper's fetch_raw_data() against the real external
# API.  Tests are marked `live` so they can be run or excluded separately.
# ===========================================================================

@pytest.mark.live
class TestNWSScraper:
    """NOAA National Weather Service active alerts — no API key required."""

    def test_fetch_raw_data(self):
        from scrapers.nws_scraper import NWSScraper

        scraper = NWSScraper()
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[NWS] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), f"[NWS] Expected list, got {type(items)}"
        print(f"\n  [NWS] SUCCESS — fetched {len(items)} active weather alert(s)")


@pytest.mark.live
class TestEPAScraper:
    """EPA Envirofacts TRI Facility data — no API key required."""

    def test_fetch_raw_data(self):
        from scrapers.epa_scraper import EPAScraper

        scraper = EPAScraper()
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[EPA] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list) and len(items) > 0, (
            f"[EPA] Expected at least one TRI facility record, got {items!r}"
        )
        print(f"\n  [EPA] SUCCESS — fetched {len(items)} TRI facility record(s)")


@pytest.mark.live
class TestAirNowScraper:
    """AirNow current air-quality observations — requires AIRNOW_API_KEY."""

    def test_fetch_raw_data(self):
        _require_env("AIRNOW_API_KEY", "AirNow scraper")

        from scrapers.airnow_scraper import AirNowScraper

        scraper = AirNowScraper()
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[AirNow] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), f"[AirNow] Expected list, got {type(items)}"
        print(f"\n  [AirNow] SUCCESS — fetched {len(items)} air quality observation(s)")


@pytest.mark.live
class TestFIRMSScraper:
    """NASA FIRMS active wildfire / hotspot data — requires NASA_FIRMS_MAP_KEY."""

    def test_fetch_raw_data(self):
        _require_env("NASA_FIRMS_MAP_KEY", "NASA FIRMS scraper")

        from scrapers.firms_scraper import FIRMSScraper

        scraper = FIRMSScraper()
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[FIRMS] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), f"[FIRMS] Expected list, got {type(items)}"
        print(f"\n  [FIRMS] SUCCESS — fetched {len(items)} fire hotspot record(s)")


# ---------------------------------------------------------------------------
# GenericAPIScraper (config-driven) live tests
# ---------------------------------------------------------------------------

@pytest.mark.live
class TestUSGSEarthquakesScraper:
    """USGS Earthquake hazards API — no API key required."""

    def test_fetch_raw_data(self):
        from scrapers.generic_api_scraper import GenericAPIScraper

        config = _load_source_config("usgs_earthquakes")
        scraper = GenericAPIScraper(config)
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[USGS Earthquakes] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), (
            f"[USGS Earthquakes] Expected list, got {type(items)}"
        )
        print(
            f"\n  [USGS Earthquakes] SUCCESS — fetched {len(items)} earthquake event(s)"
        )


@pytest.mark.live
class TestWorldBankESGScraper:
    """World Bank CO₂ Emissions (ESG) data — no API key required."""

    def test_fetch_raw_data(self):
        from scrapers.generic_api_scraper import GenericAPIScraper

        config = _load_source_config("world_bank_esg")
        scraper = GenericAPIScraper(config)
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[World Bank ESG] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list) and len(items) > 0, (
            f"[World Bank ESG] Expected at least one record, got {items!r}"
        )
        print(
            f"\n  [World Bank ESG] SUCCESS — fetched {len(items)} CO\u2082 indicator record(s)"
        )


@pytest.mark.live
class TestGBIFOccurrencesScraper:
    """GBIF invasive-species occurrence records — no API key required."""

    def test_fetch_raw_data(self):
        from scrapers.generic_api_scraper import GenericAPIScraper

        config = _load_source_config("gbif_occurrences")
        scraper = GenericAPIScraper(config)
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[GBIF Occurrences] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), (
            f"[GBIF Occurrences] Expected list, got {type(items)}"
        )
        print(
            f"\n  [GBIF Occurrences] SUCCESS — fetched {len(items)} invasive-species occurrence(s)"
        )


@pytest.mark.live
class TestOpenAQScraper:
    """OpenAQ global air-quality measurements — requires OpenAQ_API_KEY."""

    def test_fetch_raw_data(self):
        _require_env("OpenAQ_API_KEY", "OpenAQ scraper")

        from scrapers.generic_api_scraper import GenericAPIScraper

        config = _load_source_config("openaq_air_quality")
        scraper = GenericAPIScraper(config)
        try:
            items = scraper.fetch_raw_data()
        except Exception as exc:
            pytest.fail(f"[OpenAQ] fetch_raw_data() raised an error: {exc}")

        assert isinstance(items, list), f"[OpenAQ] Expected list, got {type(items)}"
        print(
            f"\n  [OpenAQ] SUCCESS — fetched {len(items)} air quality measurement(s)"
        )


# ===========================================================================
# INTERNAL API ENDPOINT TESTS
# These use an in-memory SQLite database and the FastAPI TestClient — no
# external services are called.
# ===========================================================================

class TestHealthEndpoint:
    """GET /api/v1/health — basic connectivity check."""

    def test_returns_200(self, api_client):
        resp = api_client.get("/api/v1/health")
        assert resp.status_code == 200, (
            f"[GET /api/v1/health] Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "status" in data, f"[GET /api/v1/health] 'status' key missing from response"
        print(
            f"\n  [GET /api/v1/health] SUCCESS — "
            f"status={data['status']}, database={data.get('database')}"
        )

    def test_database_field_present(self, api_client):
        resp = api_client.get("/api/v1/health")
        data = resp.json()
        assert "database" in data, (
            f"[GET /api/v1/health] 'database' key missing — got: {data}"
        )
        print(f"\n  [GET /api/v1/health] database field = '{data['database']}'")


class TestAlertsEndpoints:
    """GET /api/v1/alerts — list and stats endpoints."""

    def test_list_alerts_returns_200(self, api_client):
        resp = api_client.get("/api/v1/alerts")
        assert resp.status_code == 200, (
            f"[GET /api/v1/alerts] Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert isinstance(data, list), (
            f"[GET /api/v1/alerts] Expected list, got {type(data)}"
        )
        print(f"\n  [GET /api/v1/alerts] SUCCESS — returned {len(data)} alert(s)")

    def test_list_alerts_filter_by_type(self, api_client):
        resp = api_client.get("/api/v1/alerts", params={"alert_type": "weather"})
        assert resp.status_code == 200, (
            f"[GET /api/v1/alerts?alert_type=weather] "
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert isinstance(data, list)
        print(
            f"\n  [GET /api/v1/alerts?alert_type=weather] "
            f"SUCCESS — returned {len(data)} weather alert(s)"
        )

    def test_list_alerts_filter_by_severity(self, api_client):
        resp = api_client.get("/api/v1/alerts", params={"severity": "high"})
        assert resp.status_code == 200, (
            f"[GET /api/v1/alerts?severity=high] "
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert isinstance(data, list)
        print(
            f"\n  [GET /api/v1/alerts?severity=high] "
            f"SUCCESS — returned {len(data)} high-severity alert(s)"
        )

    def test_list_alerts_pagination(self, api_client):
        resp = api_client.get("/api/v1/alerts", params={"limit": 10, "offset": 0})
        assert resp.status_code == 200, (
            f"[GET /api/v1/alerts pagination] "
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert len(data) <= 10, (
            f"[GET /api/v1/alerts pagination] Got {len(data)} items, expected ≤10"
        )
        print(
            f"\n  [GET /api/v1/alerts pagination] "
            f"SUCCESS — returned {len(data)} alert(s) (limit=10)"
        )

    def test_alert_stats_returns_200(self, api_client):
        resp = api_client.get("/api/v1/alerts/stats")
        assert resp.status_code == 200, (
            f"[GET /api/v1/alerts/stats] Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert "total" in data, (
            f"[GET /api/v1/alerts/stats] 'total' key missing — got: {data}"
        )
        assert "by_type" in data, (
            f"[GET /api/v1/alerts/stats] 'by_type' key missing — got: {data}"
        )
        assert "by_severity" in data, (
            f"[GET /api/v1/alerts/stats] 'by_severity' key missing — got: {data}"
        )
        print(
            f"\n  [GET /api/v1/alerts/stats] SUCCESS — "
            f"total={data['total']}, by_type={data['by_type']}, by_severity={data['by_severity']}"
        )

    def test_get_nonexistent_alert_returns_404(self, api_client):
        resp = api_client.get("/api/v1/alerts/999999")
        assert resp.status_code == 404, (
            f"[GET /api/v1/alerts/999999] Expected 404, got {resp.status_code}: {resp.text}"
        )
        print(f"\n  [GET /api/v1/alerts/999999] SUCCESS — correctly returned 404")


class TestSummariesEndpoints:
    """GET /api/v1/summaries — list and latest endpoints."""

    def test_list_summaries_returns_200(self, api_client):
        resp = api_client.get("/api/v1/summaries")
        assert resp.status_code == 200, (
            f"[GET /api/v1/summaries] Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert isinstance(data, list), (
            f"[GET /api/v1/summaries] Expected list, got {type(data)}"
        )
        print(f"\n  [GET /api/v1/summaries] SUCCESS — returned {len(data)} summary(ies)")

    def test_latest_summary_returns_200(self, api_client):
        resp = api_client.get("/api/v1/summaries/latest")
        assert resp.status_code == 200, (
            f"[GET /api/v1/summaries/latest] Expected 200, got {resp.status_code}: {resp.text}"
        )
        # None is a valid response when the DB is empty
        print(
            f"\n  [GET /api/v1/summaries/latest] SUCCESS — "
            f"response={'null (none yet)' if resp.json() is None else 'summary found'}"
        )

    def test_latest_local_summary_requires_zip(self, api_client):
        """Calling /latest/local without zip_code must return 422 (validation error)."""
        resp = api_client.get("/api/v1/summaries/latest/local")
        assert resp.status_code == 422, (
            f"[GET /api/v1/summaries/latest/local (no zip)] "
            f"Expected 422, got {resp.status_code}: {resp.text}"
        )
        print(
            f"\n  [GET /api/v1/summaries/latest/local (no zip)] "
            f"SUCCESS — correctly returned 422 validation error"
        )

    def test_latest_local_summary_with_valid_zip(self, api_client):
        resp = api_client.get(
            "/api/v1/summaries/latest/local", params={"zip_code": "90001"}
        )
        assert resp.status_code == 200, (
            f"[GET /api/v1/summaries/latest/local?zip_code=90001] "
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        print(
            f"\n  [GET /api/v1/summaries/latest/local?zip_code=90001] SUCCESS — "
            f"response={'null (none yet)' if resp.json() is None else 'summary found'}"
        )


class TestRootEndpoint:
    """GET / — basic smoke test."""

    def test_root_returns_200(self, api_client):
        resp = api_client.get("/")
        assert resp.status_code == 200, (
            f"[GET /] Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        assert data.get("name") == "RiskRadar API", (
            f"[GET /] Expected name='RiskRadar API', got: {data}"
        )
        print(
            f"\n  [GET /] SUCCESS — "
            f"name={data.get('name')}, status={data.get('status')}"
        )
