"""Tests for system API endpoints."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

from auth.security import create_access_token
from db.models import NotificationDispatchLog, ScrapeLog


def _auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint(test_client, sample_alerts):
    resp = test_client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "alert_count" in data


def test_health_endpoint_includes_last_scrape(test_client, db_session, sample_alerts):
    scrape_log = ScrapeLog(
        source="nws",
        status="success",
        alerts_fetched=3,
        alerts_new=2,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(scrape_log)
    db_session.commit()

    resp = test_client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["last_scrape"]["source"] == "nws"
    assert data["last_scrape"]["status"] == "success"


def test_trigger_scrape_requires_auth(test_client):
    resp = test_client.post("/api/v1/scrape/trigger")
    assert resp.status_code == 401


def test_trigger_scrape_runs_registered_scrapers(test_client, sample_user, monkeypatch):
    class FakeScraper:
        def run(self):
            return 2

    def _fake_load_all_scrapers():
        return [
            {"id": "fake_one", "scraper": FakeScraper()},
            {"id": "fake_two", "scraper": FakeScraper()},
        ]

    monkeypatch.setattr("scrapers.registry.load_all_scrapers", _fake_load_all_scrapers)

    resp = test_client.post(
        "/api/v1/scrape/trigger",
        headers=_auth_headers(sample_user.id),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 2
    assert all(item["status"] == "success" for item in data["results"])
    assert all(item["alerts_stored"] == 2 for item in data["results"])


def test_trigger_scrape_reports_partial_failure(test_client, sample_user, monkeypatch):
    class FakeScraper:
        def run(self):
            return 2

    class FailingScraper:
        def run(self):
            raise RuntimeError("scraper exploded")

    def _fake_load_all_scrapers():
        return [
            {"id": "working", "scraper": FakeScraper()},
            {"id": "broken", "scraper": FailingScraper()},
        ]

    monkeypatch.setattr("scrapers.registry.load_all_scrapers", _fake_load_all_scrapers)

    resp = test_client.post(
        "/api/v1/scrape/trigger",
        headers=_auth_headers(sample_user.id),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["status"] == "success"
    assert data["results"][1]["status"] == "error"
    assert "scraper exploded" in data["results"][1]["error"]


def test_notify_subscribers_requires_auth(test_client, sample_alerts):
    resp = test_client.post(f"/api/v1/notifications/alerts/{sample_alerts[0].id}/notify-subscribers")
    assert resp.status_code == 401


def test_notify_subscribers_filters_by_preferences(test_client, db_session, sample_alerts, sample_user):
    sample_user.device_token = "ExponentPushToken[ok]"
    sample_user.alert_types = '["weather"]'
    sample_user.notify_severity = "high"

    other_user = type(sample_user)(
        display_name="Low Priority User",
        email="low@test.com",
        password_hash=sample_user.password_hash,
        device_token="ExponentPushToken[low]",
        alert_types='["weather"]',
        notify_severity="critical",
    )

    db_session.add(other_user)
    db_session.commit()

    resp = test_client.post(
        f"/api/v1/notifications/alerts/{sample_alerts[0].id}/notify-subscribers",
        headers=_auth_headers(sample_user.id),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "queued_stub"
    assert data["recipient_count"] == 1
    assert sample_user.id in data["recipient_user_ids"]
    assert data["provider"] == "noop"
    assert data["sent_count"] == 1
    assert data["failed_count"] == 0
    assert data["dispatch_status"] == "success"

    dispatch = db_session.query(NotificationDispatchLog).order_by(NotificationDispatchLog.id.desc()).first()
    assert dispatch is not None
    assert dispatch.alert_id == sample_alerts[0].id
    assert dispatch.provider == "noop"
    assert dispatch.recipients_total == 1
    assert dispatch.sent_count == 1
    assert dispatch.failed_count == 0
    assert dispatch.status == "success"


def test_notify_subscribers_404_for_missing_alert(test_client, sample_user):
    resp = test_client.post(
        "/api/v1/notifications/alerts/999999/notify-subscribers",
        headers=_auth_headers(sample_user.id),
    )
    assert resp.status_code == 404


def test_notify_subscribers_expo_delivery_uses_mocked_network(
    test_client,
    db_session,
    sample_alerts,
    sample_user,
    monkeypatch,
):
    sample_user.device_token = "ExponentPushToken[expo-ok]"
    sample_user.alert_types = '["weather"]'
    sample_user.notify_severity = "high"
    db_session.commit()

    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_DELIVERY_ENABLED", True)
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_TIMEOUT_SECONDS", 3.0)

    response = Mock()
    response.is_success = True
    response.status_code = 200
    response.text = "ok"

    with patch("notifications.provider.httpx.post", return_value=response) as post_mock:
        resp = test_client.post(
            f"/api/v1/notifications/alerts/{sample_alerts[0].id}/notify-subscribers",
            headers=_auth_headers(sample_user.id),
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "expo"
    assert data["recipient_count"] == 1
    assert data["sent_count"] == 1
    post_mock.assert_called_once()
