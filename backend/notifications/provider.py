"""Notification provider abstraction for backend dispatch.

This module intentionally defaults to a no-op provider so backend logic can be
validated safely before integrating external push services.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import logging
import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class NotificationProvider(Protocol):
    """Protocol for provider-specific push delivery adapters."""

    name: str

    def send(self, device_token: str, title: str, body: str) -> bool:
        """Send a push notification to a single device token."""


@dataclass(frozen=True)
class NoopNotificationProvider:
    """Safe default provider that records intent but performs no outbound calls."""

    name: str = "noop"

    def send(self, device_token: str, title: str, body: str) -> bool:
        # Intentionally succeeds to keep the dispatch pipeline deterministic in tests.
        _ = (device_token, title, body)
        return True


@dataclass(frozen=True)
class ExpoNotificationProvider:
    """Scaffold provider for future Expo push integration."""

    name: str = "expo"

    def send(self, device_token: str, title: str, body: str) -> bool:
        if not settings.NOTIFICATION_DELIVERY_ENABLED:
            logger.info("notifications.delivery_disabled provider=expo")
            return False

        payload = {
            "to": device_token,
            "title": title,
            "body": body,
            "sound": "default",
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if settings.EXPO_ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {settings.EXPO_ACCESS_TOKEN}"

        try:
            response = httpx.post(
                settings.EXPO_PUSH_URL,
                json=payload,
                headers=headers,
                timeout=settings.NOTIFICATION_TIMEOUT_SECONDS,
            )
            if response.is_success:
                return True

            logger.warning(
                "notifications.delivery_failed provider=expo status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            return False
        except Exception as exc:
            logger.warning("notifications.delivery_exception provider=expo error=%s", exc)
            return False


@dataclass(frozen=True)
class FcmNotificationProvider:
    """Scaffold provider for future Firebase Cloud Messaging integration."""

    name: str = "fcm"

    def send(self, device_token: str, title: str, body: str) -> bool:
        # Integration scaffold only: intentionally no outbound API call yet.
        _ = (device_token, title, body)
        return False


def get_notification_provider() -> NotificationProvider:
    """Return the configured notification provider adapter."""
    provider = settings.NOTIFICATION_PROVIDER.strip().lower()
    if provider in {"", "noop"}:
        return NoopNotificationProvider()

    if provider == "expo":
        if settings.EXPO_ACCESS_TOKEN:
            return ExpoNotificationProvider()
        logger.warning("notifications.provider_fallback provider=expo reason=missing_access_token")
        return NoopNotificationProvider()

    if provider == "fcm":
        if settings.FCM_SERVER_KEY and settings.FCM_PROJECT_ID:
            return FcmNotificationProvider()
        logger.warning("notifications.provider_fallback provider=fcm reason=missing_credentials")
        return NoopNotificationProvider()

    # Keep unknown provider values safe and explicit until integration is added.
    logger.warning("notifications.provider_fallback provider=%s reason=unknown", provider)
    return NoopNotificationProvider()
