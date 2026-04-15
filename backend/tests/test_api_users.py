"""Tests for user API endpoints."""

from auth.security import create_access_token, verify_password, email_hmac, hash_password
from db.models import User, SavedDestination


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
            "password": "pass123",
            "zip_code": "90210",
        })
        assert resp.status_code == 200
        assert resp.json()["zip_code"] == "90210"

    def test_password_is_hashed(self, test_client, db_session):
        email_value = "carol@test.com"
        test_client.post("/api/v1/users/register", json={
            "display_name": "Carol",
            "email": email_value,
            "password": "mypassword",
        })
        user = db_session.query(User).filter(User.email_hmac == email_hmac(email_value)).first()
        assert user.password_hash != "mypassword"
        assert verify_password("mypassword", user.password_hash)

    def test_register_does_not_store_plaintext_email(self, test_client, db_session):
        email_value = "privacy@test.com"
        test_client.post("/api/v1/users/register", json={
            "display_name": "Privacy User",
            "email": email_value,
            "password": "secret123",
        })

        user = db_session.query(User).filter(User.email_hmac == email_hmac(email_value)).first()
        assert user is not None
        assert user.email is None
        assert user.email_encrypted is not None

    def test_duplicate_email_rejected(self, test_client, sample_user):
        assert sample_user.email == "test@example.com"
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Duplicate",
            "email": "test@example.com",
            "password": "pass123",
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    def test_register_invalid_email_rejected(self, test_client):
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Bad Email",
            "email": "not-an-email",
            "password": "secret123",
        })
        assert resp.status_code == 422

    def test_register_invalid_zip_rejected(self, test_client):
        resp = test_client.post("/api/v1/users/register", json={
            "display_name": "Bad Zip",
            "email": "zip@test.com",
            "password": "secret123",
            "zip_code": "12AB",
        })
        assert resp.status_code == 422


class TestLoginUser:
    def test_login_success(self, test_client, sample_user):
        assert sample_user.id is not None
        resp = test_client.post("/api/v1/users/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password_rejected(self, test_client, sample_user):
        assert sample_user.display_name == "Test User"
        resp = test_client.post("/api/v1/users/login", json={
            "email": "test@example.com",
            "password": "wrong-password",
        })
        assert resp.status_code == 401
        assert "Invalid email or password" in resp.json()["detail"]

    def test_login_unknown_email_rejected(self, test_client):
        resp = test_client.post("/api/v1/users/login", json={
            "email": "missing@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401

    def test_login_legacy_plaintext_email_user_still_supported(self, test_client, db_session):
        legacy_user = User(
            display_name="Legacy",
            email="legacy_login@test.com",
            email_encrypted=None,
            email_hmac=None,
            password_hash=hash_password("legacy-pass"),
        )
        db_session.add(legacy_user)
        db_session.commit()

        resp = test_client.post("/api/v1/users/login", json={
            "email": "legacy_login@test.com",
            "password": "legacy-pass",
        })

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data


class TestCurrentUserAndNotifications:
    def test_me_requires_auth(self, test_client):
        resp = test_client.get("/api/v1/users/me")
        assert resp.status_code == 401

    def test_me_returns_current_user(self, test_client, sample_user):
        resp = test_client.get("/api/v1/users/me", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "Test User"

    def test_get_preferences_requires_own_user(self, test_client, sample_user):
        resp = test_client.get(f"/api/v1/users/{sample_user.id}/preferences", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_get_preferences_for_other_user_forbidden(self, test_client, sample_user):
        resp = test_client.get("/api/v1/users/9999/preferences", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 403

    def test_get_notifications_returns_settings(self, test_client, sample_user):
        resp = test_client.get("/api/v1/users/notifications", headers=_auth_headers(sample_user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert data["notify_severity"] == "high"
        assert data["notify_push"] is True
        assert data["notify_email"] is False
        assert data["notify_sms"] is False
        assert data["device_token"] is None

    def test_update_notifications(self, test_client, sample_user, db_session):
        resp = test_client.put(
            "/api/v1/users/notifications",
            json={
                "notify_severity": "critical",
                "notify_push": False,
                "notify_email": True,
                "notify_sms": True,
                "device_token": "device-123",
            },
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["notify_severity"] == "critical"
        assert data["notify_push"] is False
        assert data["notify_email"] is True
        assert data["notify_sms"] is True
        assert data["device_token"] == "device-123"

        user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert user.notify_severity == "critical"
        assert user.notify_push is False
        assert user.notify_email is True
        assert user.notify_sms is True
        assert user.device_token == "device-123"


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

    def test_update_notification_channels(self, test_client, sample_user, db_session):
        resp = test_client.put(
            f"/api/v1/users/{sample_user.id}/preferences",
            json={"notify_push": False, "notify_email": True, "notify_sms": True},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["notify_push"] is False
        assert data["notify_email"] is True
        assert data["notify_sms"] is True

        user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert user.notify_push is False
        assert user.notify_email is True
        assert user.notify_sms is True

    def test_update_forbidden_for_other_user(self, test_client, sample_user):
        resp = test_client.put("/api/v1/users/9999/preferences", json={
            "zip_code": "00000",
        }, headers=_auth_headers(sample_user.id))
        assert resp.status_code == 403

    def test_update_invalid_notify_severity_rejected(self, test_client, sample_user):
        resp = test_client.put(
            f"/api/v1/users/{sample_user.id}/preferences",
            json={"notify_severity": "urgent"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 422

    def test_update_invalid_alert_types_rejected(self, test_client, sample_user):
        resp = test_client.put(
            f"/api/v1/users/{sample_user.id}/preferences",
            json={"alert_types": ["weather", "bad_type"]},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 422

    def test_update_device_token_via_preferences(self, test_client, sample_user, db_session):
        """PUT /{id}/preferences with device_token stores the token on the User row."""
        resp = test_client.put(f"/api/v1/users/{sample_user.id}/preferences", json={
            "device_token": "tok_abc123",
        }, headers=_auth_headers(sample_user.id))

        assert resp.status_code == 200
        # Confirm it is persisted in the DB
        db_session.refresh(sample_user)
        assert sample_user.device_token == "tok_abc123"

    def test_update_device_token_overwrite(self, test_client, sample_user, db_session):
        """A second PUT replaces the previous device_token."""
        test_client.put(f"/api/v1/users/{sample_user.id}/preferences", json={
            "device_token": "old_token",
        }, headers=_auth_headers(sample_user.id))

        resp = test_client.put(f"/api/v1/users/{sample_user.id}/preferences", json={
            "device_token": "new_token",
        }, headers=_auth_headers(sample_user.id))

        assert resp.status_code == 200
        db_session.refresh(sample_user)
        assert sample_user.device_token == "new_token"


class TestDeviceTokenManagement:
    def test_register_device_token(self, test_client, sample_user, db_session):
        resp = test_client.post(
            f"/api/v1/users/{sample_user.id}/device-token",
            json={"device_token": "ExponentPushToken[abc123]"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["device_token"] == "ExponentPushToken[abc123]"

        user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert user.device_token == "ExponentPushToken[abc123]"

    def test_register_blank_device_token_rejected(self, test_client, sample_user):
        resp = test_client.post(
            f"/api/v1/users/{sample_user.id}/device-token",
            json={"device_token": "   "},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 422

    def test_revoke_device_token(self, test_client, sample_user, db_session):
        sample_user.device_token = "ExponentPushToken[seed]"
        db_session.commit()

        resp = test_client.post(
            f"/api/v1/users/{sample_user.id}/device-token/revoke",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["device_token"] is None

        user = db_session.query(User).filter(User.id == sample_user.id).first()
        assert user.device_token is None

    def test_register_device_token_other_user_forbidden(self, test_client, sample_user):
        resp = test_client.post(
            "/api/v1/users/9999/device-token",
            json={"device_token": "ExponentPushToken[abc123]"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Notification settings
# ---------------------------------------------------------------------------

class TestNotificationSettings:
    def test_get_notifications_defaults(self, test_client, sample_user):
        """GET /notifications returns the user's current notification fields."""
        resp = test_client.get(
            "/api/v1/users/notifications",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        # Keys must be present (values may be None for a fresh user)
        assert "notify_severity" in data
        assert "device_token" in data

    def test_put_notifications_saves_device_token(self, test_client, sample_user, db_session):
        """PUT /notifications with device_token persists the token."""
        resp = test_client.put(
            "/api/v1/users/notifications",
            json={"device_token": "fcm_token_xyz"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["device_token"] == "fcm_token_xyz"

        # Verify DB row is updated
        db_session.refresh(sample_user)
        assert sample_user.device_token == "fcm_token_xyz"

    def test_put_notifications_saves_severity(self, test_client, sample_user, db_session):
        """PUT /notifications with notify_severity persists the severity level."""
        resp = test_client.put(
            "/api/v1/users/notifications",
            json={"notify_severity": "moderate"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["notify_severity"] == "moderate"

        db_session.refresh(sample_user)
        assert sample_user.notify_severity == "moderate"

    def test_put_notifications_saves_both_fields(self, test_client, sample_user, db_session):
        """PUT /notifications can set device_token and notify_severity together."""
        resp = test_client.put(
            "/api/v1/users/notifications",
            json={"device_token": "tok_both", "notify_severity": "low"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["device_token"] == "tok_both"
        assert data["notify_severity"] == "low"

    def test_put_notifications_device_token_reflected_in_get(self, test_client, sample_user):
        """After a PUT, a subsequent GET returns the new device_token."""
        test_client.put(
            "/api/v1/users/notifications",
            json={"device_token": "reflect_me"},
            headers=_auth_headers(sample_user.id),
        )
        resp = test_client.get(
            "/api/v1/users/notifications",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["device_token"] == "reflect_me"

    def test_put_notifications_requires_auth(self, test_client):
        """PUT /notifications without a JWT returns 401."""
        resp = test_client.put(
            "/api/v1/users/notifications",
            json={"device_token": "no_auth"},
        )
        assert resp.status_code == 401

    def test_get_notifications_requires_auth(self, test_client):
        """GET /notifications without a JWT returns 401."""
        resp = test_client.get("/api/v1/users/notifications")
        assert resp.status_code == 401

    def test_put_notifications_empty_body_is_noop(self, test_client, sample_user, db_session):
        """PUT /notifications with no fields doesn't change existing values."""
        # Seed a token first
        sample_user.device_token = "keep_me"
        db_session.commit()

        resp = test_client.put(
            "/api/v1/users/notifications",
            json={},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        # Token should remain unchanged
        db_session.refresh(sample_user)
        assert sample_user.device_token == "keep_me"


# ---------------------------------------------------------------------------
# Saved destinations — POST
# ---------------------------------------------------------------------------

class TestSaveDestination:
    def test_save_destination_success(self, test_client, sample_user):
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Denver", "state": "CO", "latitude": 39.74, "longitude": -104.98},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["city"] == "Denver"
        assert data["state"] == "CO"
        assert data["latitude"] == 39.74
        assert data["longitude"] == -104.98
        assert "id" in data
        assert "created_at" in data

    def test_save_destination_with_zip(self, test_client, sample_user):
        """zip_code is optional; when provided it is stored and returned."""
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Austin", "state": "TX", "zip_code": "73301", "latitude": 30.27, "longitude": -97.74},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["zip_code"] == "73301"

    def test_save_destination_without_state(self, test_client, sample_user):
        """state is optional and may be omitted."""
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Honolulu", "latitude": 21.31, "longitude": -157.86},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["city"] == "Honolulu"
        assert resp.json()["state"] is None

    def test_save_duplicate_destination_returns_409(self, test_client, sample_user):
        """POSTing the same city+state twice returns 409 Conflict."""
        payload = {"city": "Chicago", "state": "IL", "latitude": 41.88, "longitude": -87.63}
        test_client.post(
            "/api/v1/users/destinations",
            json=payload,
            headers=_auth_headers(sample_user.id),
        )
        resp = test_client.post(
            "/api/v1/users/destinations",
            json=payload,
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 409
        assert "already saved" in resp.json()["detail"]

    def test_save_destination_requires_auth(self, test_client):
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Portland", "state": "OR", "latitude": 45.52, "longitude": -122.68},
        )
        assert resp.status_code == 401

    def test_save_destination_missing_required_fields_returns_422(self, test_client, sample_user):
        """latitude and longitude are required; omitting them yields 422."""
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Miami"},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 422

    def test_same_city_different_state_is_not_duplicate(self, test_client, sample_user):
        """Portland OR and Portland ME are distinct destinations."""
        test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Portland", "state": "OR", "latitude": 45.52, "longitude": -122.68},
            headers=_auth_headers(sample_user.id),
        )
        resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Portland", "state": "ME", "latitude": 43.66, "longitude": -70.26},
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200

    def test_destinations_are_user_scoped(self, test_client, sample_user, db_session):
        """Two different users can both save the same city without conflict."""
        from db.models import User
        from auth.security import hash_password, encrypt_email, email_hmac

        other = User(
            display_name="Other",
            email=None,
            email_encrypted=encrypt_email("other@test.com"),
            email_hmac=email_hmac("other@test.com"),
            password_hash=hash_password("pass123"),
        )
        db_session.add(other)
        db_session.commit()
        db_session.refresh(other)

        payload = {"city": "Seattle", "state": "WA", "latitude": 47.61, "longitude": -122.33}
        r1 = test_client.post(
            "/api/v1/users/destinations", json=payload, headers=_auth_headers(sample_user.id)
        )
        r2 = test_client.post(
            "/api/v1/users/destinations", json=payload, headers=_auth_headers(other.id)
        )
        assert r1.status_code == 200
        assert r2.status_code == 200


# ---------------------------------------------------------------------------
# Saved destinations — GET
# ---------------------------------------------------------------------------

class TestListDestinations:
    def test_list_empty_destinations(self, test_client, sample_user):
        resp = test_client.get(
            "/api/v1/users/destinations",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_saved_destinations(self, test_client, sample_user):
        test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Boston", "state": "MA", "latitude": 42.36, "longitude": -71.06},
            headers=_auth_headers(sample_user.id),
        )
        resp = test_client.get(
            "/api/v1/users/destinations",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["city"] == "Boston"

    def test_list_multiple_destinations(self, test_client, sample_user):
        for city, state, lat, lon in [
            ("Phoenix", "AZ", 33.45, -112.07),
            ("Nashville", "TN", 36.17, -86.78),
            ("Baltimore", "MD", 39.29, -76.61),
        ]:
            test_client.post(
                "/api/v1/users/destinations",
                json={"city": city, "state": state, "latitude": lat, "longitude": lon},
                headers=_auth_headers(sample_user.id),
            )

        resp = test_client.get(
            "/api/v1/users/destinations",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_only_returns_own_destinations(self, test_client, sample_user, db_session):
        """GET /destinations must not return destinations belonging to other users."""
        from db.models import User
        from auth.security import hash_password, encrypt_email, email_hmac

        other = User(
            display_name="Other2",
            email=None,
            email_encrypted=encrypt_email("other2@test.com"),
            email_hmac=email_hmac("other2@test.com"),
            password_hash=hash_password("pass123"),
        )
        db_session.add(other)
        db_session.commit()
        db_session.refresh(other)

        # other user saves a destination
        test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Dallas", "state": "TX", "latitude": 32.78, "longitude": -96.80},
            headers=_auth_headers(other.id),
        )
        # sample_user's list should be empty
        resp = test_client.get(
            "/api/v1/users/destinations",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_destinations_requires_auth(self, test_client):
        resp = test_client.get("/api/v1/users/destinations")
        assert resp.status_code == 401

    def test_list_destinations_ordered_most_recent_first(self, test_client, sample_user):
        """Destinations are returned newest-first (order_by created_at desc)."""
        for city, state, lat, lon in [
            ("Atlanta", "GA", 33.75, -84.39),
            ("Minneapolis", "MN", 44.98, -93.27),
        ]:
            test_client.post(
                "/api/v1/users/destinations",
                json={"city": city, "state": state, "latitude": lat, "longitude": lon},
                headers=_auth_headers(sample_user.id),
            )

        resp = test_client.get(
            "/api/v1/users/destinations",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 200
        cities = [d["city"] for d in resp.json()]
        # Minneapolis was saved last so it should appear first
        assert cities[0] == "Minneapolis"


# ---------------------------------------------------------------------------
# Saved destinations — DELETE
# ---------------------------------------------------------------------------

class TestDeleteDestination:
    def test_delete_destination_success(self, test_client, sample_user, db_session):
        post_resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Las Vegas", "state": "NV", "latitude": 36.17, "longitude": -115.14},
            headers=_auth_headers(sample_user.id),
        )
        dest_id = post_resp.json()["id"]

        del_resp = test_client.delete(
            f"/api/v1/users/destinations/{dest_id}",
            headers=_auth_headers(sample_user.id),
        )
        assert del_resp.status_code == 200
        assert "removed" in del_resp.json()["detail"].lower()

        # Confirm it is gone from DB
        assert db_session.get(SavedDestination, dest_id) is None

    def test_delete_nonexistent_destination_returns_404(self, test_client, sample_user):
        resp = test_client.delete(
            "/api/v1/users/destinations/99999",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 404

    def test_delete_requires_auth(self, test_client, sample_user):
        post_resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Reno", "state": "NV", "latitude": 39.53, "longitude": -119.81},
            headers=_auth_headers(sample_user.id),
        )
        dest_id = post_resp.json()["id"]

        resp = test_client.delete(f"/api/v1/users/destinations/{dest_id}")
        assert resp.status_code == 401

    def test_cannot_delete_another_users_destination(self, test_client, sample_user, db_session):
        """A user must not be able to delete a destination owned by another user."""
        from db.models import User
        from auth.security import hash_password, encrypt_email, email_hmac

        other = User(
            display_name="Other3",
            email=None,
            email_encrypted=encrypt_email("other3@test.com"),
            email_hmac=email_hmac("other3@test.com"),
            password_hash=hash_password("pass123"),
        )
        db_session.add(other)
        db_session.commit()
        db_session.refresh(other)

        # other user saves a destination
        post_resp = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Tampa", "state": "FL", "latitude": 27.95, "longitude": -82.46},
            headers=_auth_headers(other.id),
        )
        dest_id = post_resp.json()["id"]

        # sample_user tries to delete it — must get 404 (not found for this user)
        resp = test_client.delete(
            f"/api/v1/users/destinations/{dest_id}",
            headers=_auth_headers(sample_user.id),
        )
        assert resp.status_code == 404

        # Destination should still exist in DB
        assert db_session.get(SavedDestination, dest_id) is not None

    def test_delete_removes_only_target_destination(self, test_client, sample_user, db_session):
        """Deleting one destination leaves others intact."""
        r1 = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Tucson", "state": "AZ", "latitude": 32.22, "longitude": -110.97},
            headers=_auth_headers(sample_user.id),
        )
        r2 = test_client.post(
            "/api/v1/users/destinations",
            json={"city": "Albuquerque", "state": "NM", "latitude": 35.08, "longitude": -106.65},
            headers=_auth_headers(sample_user.id),
        )
        id_to_delete = r1.json()["id"]
        id_to_keep = r2.json()["id"]

        test_client.delete(
            f"/api/v1/users/destinations/{id_to_delete}",
            headers=_auth_headers(sample_user.id),
        )

        assert db_session.get(SavedDestination, id_to_delete) is None
        assert db_session.get(SavedDestination, id_to_keep) is not None
