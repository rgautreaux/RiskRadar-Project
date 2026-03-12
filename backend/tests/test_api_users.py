"""Tests for user API endpoints."""

from auth.security import create_access_token, verify_password


def _auth_headers(user_id: int) -> dict[str, str]:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


class TestRegisterUser:
    def test_register_success(self, test_client):
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Alice",
            "email": "alice@test.com",
            "password": "secret123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] == "Alice"
        assert data["email"] == "alice@test.com"
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_with_zip(self, test_client):
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Bob",
            "email": "bob@test.com",
            "password": "pass",
            "zip_code": "90210",
        })
        assert resp.status_code == 200
        assert resp.json()["zip_code"] == "90210"

    def test_password_is_hashed(self, test_client, db_session):
        from db.models import User

        test_client.post("/api/v1/users/register", json={
            "display_name": "Carol",
            "email": "carol@test.com",
            "password": "mypassword",
        })
        user = db_session.query(User).filter(User.email == "carol@test.com").first()
        assert user.password_hash != "mypassword"
        assert verify_password("mypassword", user.password_hash)

    def test_duplicate_email_rejected(self, test_client, sample_user):
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Duplicate",
            "email": "test@example.com",
            "password": "pass",
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]


class TestUpdatePreferences:
    def test_update_zip_code(self, test_client, sample_user):
        resp = test_client.put(f"/api/v1/users/{sample_user.id}/preferences", json={
            "zip_code": "10001",
        }, headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        assert resp.json()["zip_code"] == "10001"

    def test_update_alert_types(self, test_client, sample_user):
        resp = test_client.put(f"/api/v1/users/{sample_user.id}/preferences", json={
            "alert_types": ["weather", "earthquake"],
        }, headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200

    def test_update_forbidden_for_other_user(self, test_client, sample_user):
        resp = test_client.put("/api/v1/users/9999/preferences", json={
            "zip_code": "00000",
        }, headers=_auth_headers(sample_user.id))
        assert resp.status_code == 403
