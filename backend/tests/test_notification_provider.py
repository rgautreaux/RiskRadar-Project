"""Tests for notification provider selection and fallback behavior."""

from unittest.mock import Mock, patch

from notifications.provider import get_notification_provider


def test_default_provider_is_noop(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "")
    provider = get_notification_provider()
    assert provider.name == "noop"


def test_expo_falls_back_without_token(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "")
    provider = get_notification_provider()
    assert provider.name == "noop"


def test_expo_provider_selected_with_token(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    provider = get_notification_provider()
    assert provider.name == "expo"


def test_expo_send_returns_false_when_delivery_disabled(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_DELIVERY_ENABLED", False)
    provider = get_notification_provider()

    with patch("notifications.provider.httpx.post") as post_mock:
        sent = provider.send("ExponentPushToken[test]", "Title", "Body")

    assert sent is False
    post_mock.assert_not_called()


def test_expo_send_returns_true_on_success(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_DELIVERY_ENABLED", True)
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_TIMEOUT_SECONDS", 5.0)
    provider = get_notification_provider()

    response = Mock()
    response.is_success = True
    response.status_code = 200
    response.text = "ok"

    with patch("notifications.provider.httpx.post", return_value=response) as post_mock:
        sent = provider.send("ExponentPushToken[test]", "Title", "Body")

    assert sent is True
    post_mock.assert_called_once()


def test_expo_send_returns_false_on_http_error(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_DELIVERY_ENABLED", True)
    provider = get_notification_provider()

    response = Mock()
    response.is_success = False
    response.status_code = 503
    response.text = "service unavailable"

    with patch("notifications.provider.httpx.post", return_value=response):
        sent = provider.send("ExponentPushToken[test]", "Title", "Body")

    assert sent is False


def test_expo_send_returns_false_on_exception(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "expo")
    monkeypatch.setattr("config.settings.settings.EXPO_ACCESS_TOKEN", "token")
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_DELIVERY_ENABLED", True)
    provider = get_notification_provider()

    with patch("notifications.provider.httpx.post", side_effect=RuntimeError("network down")):
        sent = provider.send("ExponentPushToken[test]", "Title", "Body")

    assert sent is False


def test_fcm_falls_back_without_credentials(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "fcm")
    monkeypatch.setattr("config.settings.settings.FCM_SERVER_KEY", "")
    monkeypatch.setattr("config.settings.settings.FCM_PROJECT_ID", "")
    provider = get_notification_provider()
    assert provider.name == "noop"


def test_fcm_provider_selected_with_credentials(monkeypatch):
    monkeypatch.setattr("config.settings.settings.NOTIFICATION_PROVIDER", "fcm")
    monkeypatch.setattr("config.settings.settings.FCM_SERVER_KEY", "server-key")
    monkeypatch.setattr("config.settings.settings.FCM_PROJECT_ID", "project-id")
    provider = get_notification_provider()
    assert provider.name == "fcm"
