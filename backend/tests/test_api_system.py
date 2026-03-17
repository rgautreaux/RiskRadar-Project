"""Tests for system API endpoints."""

from auth.security import create_access_token


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
