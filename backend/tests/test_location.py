"""Tests for location-based alert ingestion."""

from db.models import Alert


def _location_alert(source: str, source_id: str, title: str) -> dict:
    return {
        "source": source,
        "source_id": source_id,
        "alert_type": "weather" if source == "nws" else "air_quality",
        "severity": "high" if source == "nws" else "moderate",
        "title": title,
        "description": f"{title} description",
        "latitude": 34.05,
        "longitude": -118.24,
        "location_name": "Los Angeles, CA",
        "event_start": "2026-04-10T12:00:00Z",
        "event_end": None,
    }


class TestLocationAlerts:
    def test_get_alerts_for_location(self, test_client, db_session, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))
        monkeypatch.setattr(
            "api.location._fetch_nws_alerts",
            lambda lat, lon, state: [_location_alert("nws", "nws_001", "Local Severe Weather")],
        )
        monkeypatch.setattr(
            "api.location._fetch_airnow",
            lambda zip_code: [_location_alert("airnow", f"{zip_code}_PM25_2026-04-10", "Local Air Quality")],
        )

        resp = test_client.get("/api/v1/location/alerts?zip_code=90001")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert {item["source"] for item in data} == {"nws", "airnow"}
        assert db_session.query(Alert).count() == 2

    def test_get_alerts_for_location_deduplicates_on_repeat(self, test_client, db_session, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))
        monkeypatch.setattr(
            "api.location._fetch_nws_alerts",
            lambda lat, lon, state: [_location_alert("nws", "nws_001", "Local Severe Weather")],
        )
        monkeypatch.setattr(
            "api.location._fetch_airnow",
            lambda zip_code: [_location_alert("airnow", f"{zip_code}_PM25_2026-04-10", "Local Air Quality")],
        )

        first = test_client.get("/api/v1/location/alerts?zip_code=90001")
        second = test_client.get("/api/v1/location/alerts?zip_code=90001")

        assert first.status_code == 200
        assert second.status_code == 200
        assert len(first.json()) == 2
        assert len(second.json()) == 2
        assert db_session.query(Alert).count() == 2

    def test_get_alerts_for_location_invalid_zip(self, test_client):
        resp = test_client.get("/api/v1/location/alerts?zip_code=90")
        assert resp.status_code == 400
        assert "Invalid zip code" in resp.json()["detail"]

    def test_get_alerts_for_location_unknown_zip(self, test_client, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: None)

        resp = test_client.get("/api/v1/location/alerts?zip_code=99999")
        assert resp.status_code == 404
        assert "Could not find location" in resp.json()["detail"]


class TestLocationInfo:
    def test_get_location_info(self, test_client, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))

        resp = test_client.get("/api/v1/location/info?zip_code=90001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["city"] == "Los Angeles"
        assert data["state"] == "CA"

    def test_get_location_info_invalid_zip(self, test_client):
        resp = test_client.get("/api/v1/location/info?zip_code=abc")
        assert resp.status_code == 400