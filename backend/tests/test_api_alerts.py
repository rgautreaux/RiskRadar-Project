"""Tests for alert API endpoints."""

import json

from auth.security import create_access_token


def _auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


class TestListAlerts:
    def test_list_all(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_filter_by_alert_type(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts?alert_type=weather")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["alert_type"] == "weather"

    def test_filter_by_severity(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts?severity=moderate")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["severity"] == "moderate"

    def test_filter_by_source(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts?source=epa")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["source"] == "epa"

    def test_pagination_limit(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts?limit=2")
        data = resp.json()
        assert len(data) == 2

    def test_pagination_offset(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts?limit=2&offset=2")
        data = resp.json()
        assert len(data) == 1

    def test_empty_database(self, test_client):
        resp = test_client.get("/api/v1/alerts")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_invalid_alert_type_rejected(self, test_client):
        resp = test_client.get("/api/v1/alerts?alert_type=bad")
        assert resp.status_code == 422

    def test_invalid_severity_rejected(self, test_client):
        resp = test_client.get("/api/v1/alerts?severity=urgent")
        assert resp.status_code == 422

    def test_negative_offset_rejected(self, test_client):
        resp = test_client.get("/api/v1/alerts?offset=-1")
        assert resp.status_code == 422

    def test_preference_filter_applies_for_authenticated_user(self, test_client, sample_alerts, sample_user, db_session):
        sample_user.alert_types = json.dumps(["weather"])
        sample_user.notify_severity = "high"
        db_session.commit()

        resp = test_client.get("/api/v1/alerts", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["alert_type"] == "weather"

    def test_query_override_beats_user_preference(self, test_client, sample_alerts, sample_user, db_session):
        sample_user.alert_types = json.dumps(["weather"])
        db_session.commit()

        resp = test_client.get("/api/v1/alerts?alert_type=pollution", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["alert_type"] == "pollution"


class TestAlertStats:
    def test_stats(self, test_client, sample_alerts):
        resp = test_client.get("/api/v1/alerts/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["by_type"]["weather"] == 1
        assert data["by_type"]["pollution"] == 1
        assert data["by_type"]["earthquake"] == 1
        assert data["by_severity"]["high"] == 1
        assert data["by_severity"]["moderate"] == 1
        assert data["by_severity"]["low"] == 1

    def test_stats_empty(self, test_client):
        resp = test_client.get("/api/v1/alerts/stats")
        data = resp.json()
        assert data["total"] == 0


class TestGetAlert:
    def test_get_by_id(self, test_client, sample_alerts):
        alert_id = sample_alerts[0].id
        resp = test_client.get(f"/api/v1/alerts/{alert_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Severe Thunderstorm Warning"

    def test_not_found(self, test_client):
        resp = test_client.get("/api/v1/alerts/9999")
        assert resp.status_code == 404
