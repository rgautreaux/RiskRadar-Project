"""Tests for the forecast ZIP endpoint.

Covers GET /api/v1/forecast/zip?zip_code=...

Strategy:
  - _zip_to_coords and get_forecast both make live HTTP calls, so they are
    patched at the module level where they are imported/called inside forecast.py.
  - The forecast cache (_cache) is cleared between tests so cache hits from
    one test cannot bleed into the next.
"""

from unittest.mock import patch

import pytest

from api.forecast import _cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A minimal valid ForecastPeriodOut payload to return from the mocked
# get_forecast. All required fields must be present.
_FAKE_PERIOD = {
    "name": "Tonight",
    "temperature": 65,
    "temperature_unit": "F",
    "wind_speed": "5 mph",
    "wind_direction": "NW",
    "short_forecast": "Clear",
    "detailed_forecast": "Clear skies tonight.",
    "is_daytime": False,
    "start_time": "2026-04-08T18:00:00-07:00",
    "end_time": "2026-04-09T06:00:00-07:00",
    "icon": "https://api.weather.gov/icons/land/night/skc",
    "precipitation_chance": None,
}

_FAKE_COORDS = (34.05, -118.24, "Los Angeles", "CA")  # (lat, lon, city, state)


@pytest.fixture(autouse=True)
def clear_forecast_cache():
    """Ensure the module-level LRU cache is empty before each test."""
    _cache.clear()
    yield
    _cache.clear()


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestForecastByZip:
    def test_returns_forecast_for_valid_zip(self, test_client):
        with (
            patch("api.forecast._zip_to_coords", return_value=_FAKE_COORDS),
            patch("api.forecast.get_forecast", return_value=[_FAKE_PERIOD]),
        ):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=90001")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Tonight"
        assert data[0]["temperature"] == 65

    def test_passes_correct_lat_lon_to_get_forecast(self, test_client):
        """Verify that the lat/lon unpacked from _zip_to_coords are forwarded."""
        captured = {}

        def fake_get_forecast(lat, lon):
            captured["lat"] = lat
            captured["lon"] = lon
            return [_FAKE_PERIOD]

        with (
            patch("api.forecast._zip_to_coords", return_value=_FAKE_COORDS),
            patch("api.forecast.get_forecast", side_effect=fake_get_forecast),
        ):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=90001")

        assert resp.status_code == 200
        assert captured["lat"] == 34.05
        assert captured["lon"] == -118.24

    def test_returns_multiple_periods(self, test_client):
        periods = [
            {**_FAKE_PERIOD, "name": "Tonight"},
            {**_FAKE_PERIOD, "name": "Thursday", "is_daytime": True},
        ]
        with (
            patch("api.forecast._zip_to_coords", return_value=_FAKE_COORDS),
            patch("api.forecast.get_forecast", return_value=periods),
        ):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=90001")

        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_response_includes_precipitation_chance_when_present(self, test_client):
        period_with_precip = {**_FAKE_PERIOD, "precipitation_chance": 40}
        with (
            patch("api.forecast._zip_to_coords", return_value=_FAKE_COORDS),
            patch("api.forecast.get_forecast", return_value=[period_with_precip]),
        ):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=90001")

        assert resp.status_code == 200
        assert resp.json()[0]["precipitation_chance"] == 40


# ---------------------------------------------------------------------------
# Error / edge-case tests
# ---------------------------------------------------------------------------

class TestForecastByZipErrors:
    def test_unknown_zip_returns_404(self, test_client):
        with patch("api.forecast._zip_to_coords", return_value=None):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=00000")

        assert resp.status_code == 404
        assert "00000" in resp.json()["detail"]

    def test_missing_zip_query_param_returns_422(self, test_client):
        resp = test_client.get("/api/v1/forecast/zip")
        assert resp.status_code == 422

    def test_zip_code_appears_in_404_detail(self, test_client):
        with patch("api.forecast._zip_to_coords", return_value=None):
            resp = test_client.get("/api/v1/forecast/zip?zip_code=12345")

        detail = resp.json()["detail"]
        assert "12345" in detail

    def test_zip_to_coords_called_once_per_request(self, test_client):
        """_zip_to_coords should be called exactly once per GET /forecast/zip call."""
        with (
            patch("api.forecast._zip_to_coords", return_value=_FAKE_COORDS) as mock_coords,
            patch("api.forecast.get_forecast", return_value=[_FAKE_PERIOD]),
        ):
            test_client.get("/api/v1/forecast/zip?zip_code=90001")
            assert mock_coords.call_count == 1
