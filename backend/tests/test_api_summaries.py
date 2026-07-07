"""Tests for summary API endpoints."""

import json
from unittest.mock import patch, MagicMock

from db.models import Summary


def _mock_local_alert(source: str, source_id: str, title: str) -> dict:
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


class TestListSummaries:
    def test_list_all(self, test_client, sample_summary):
        resp = test_client.get("/api/v1/summaries")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["summary_type"] == "daily"

    def test_filter_by_type(self, test_client, sample_summary):
        resp = test_client.get("/api/v1/summaries?summary_type=daily")
        data = resp.json()
        assert len(data) == 1

    def test_filter_no_match(self, test_client, sample_summary):
        resp = test_client.get("/api/v1/summaries?summary_type=breaking")
        data = resp.json()
        assert len(data) == 0

    def test_empty_database(self, test_client):
        resp = test_client.get("/api/v1/summaries")
        assert resp.status_code == 200
        assert resp.json() == []


class TestLatestSummary:
    def test_returns_latest(self, test_client, sample_summary):
        resp = test_client.get("/api/v1/summaries/latest")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == sample_summary.title

    def test_returns_null_when_empty(self, test_client):
        resp = test_client.get("/api/v1/summaries/latest")
        assert resp.status_code == 200
        assert resp.json() is None


class TestLatestLocalSummary:
    def test_returns_latest_local(self, test_client, db_session, sample_alerts):
        local_summary = Summary(
            title="Local Digest for Los Angeles, CA — Mar 27, 2026",
            content="## Executive Summary\nLocal alerts for LA.",
            summary_type="local",
            alert_ids=json.dumps([sample_alerts[0].id]),
            region="Los Angeles, CA 90001",
            model_used="openai/gpt-5.2",
            token_count=80,
        )
        db_session.add(local_summary)
        db_session.commit()
        db_session.refresh(local_summary)

        resp = test_client.get("/api/v1/summaries/latest/local?zip_code=90001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary_type"] == "local"
        assert "Los Angeles" in data["title"]

    def test_returns_null_when_no_local(self, test_client):
        resp = test_client.get("/api/v1/summaries/latest/local?zip_code=90001")
        assert resp.status_code == 200
        assert resp.json() is None

    def test_rejects_invalid_zip(self, test_client):
        resp = test_client.get("/api/v1/summaries/latest/local?zip_code=abc")
        assert resp.status_code == 422


class TestGenerateSummary:
    def test_generate_with_alerts(self, test_client, sample_alerts):
        mock_return = ("## Daily Digest\nTest summary content.", 100, "openai/gpt-5.2")
        with patch("llm.summarizer.Summarizer._call_llm", return_value=mock_return):
            resp = test_client.post("/api/v1/summaries/generate")
        assert resp.status_code == 200
        data = resp.json()
        assert "Daily Digest" in data["content"]
        assert data["summary_type"] == "daily"

    def test_generate_no_alerts(self, test_client):
        resp = test_client.post("/api/v1/summaries/generate")
        assert resp.status_code == 404

    def test_generate_falls_back_when_llm_fails(self, test_client, sample_alerts):
        with patch("llm.summarizer.Summarizer._call_llm", side_effect=RuntimeError("provider down")):
            resp = test_client.post("/api/v1/summaries/generate")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary_type"] == "daily"
        # The fallback copy reassures the user without using the word "fallback" —
        # it points them at the Alerts tab so they can still get critical info
        # while the LLM is down. `model_used` is the contract for "was this a
        # fallback?" — keep asserting that rather than the user-facing string.
        assert data["model_used"] == "fallback-no-llm"
        assert "briefing service is temporarily unavailable" in data["content"]


class TestLocalSummaryFlow:
    def test_generate_local_summary(self, test_client, db_session, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))
        monkeypatch.setattr(
            "api.location._fetch_nws_alerts",
            lambda lat, lon, state: [_mock_local_alert("nws", "nws_001", "Local Severe Weather")],
        )
        monkeypatch.setattr(
            "api.location._fetch_airnow",
            lambda zip_code: [_mock_local_alert("airnow", f"{zip_code}_PM25_2026-04-10", "Local Air Quality")],
        )

        mock_return = ("## Local Digest\nTest local summary.", 42, "openai/gpt-5.2")
        with patch("llm.summarizer.Summarizer._call_llm", return_value=mock_return):
            resp = test_client.post("/api/v1/summaries/generate/local?zip_code=90001")

        assert resp.status_code == 200
        data = resp.json()
        assert data["summary_type"] == "local"
        assert data["region"] == "Los Angeles, CA 90001"
        # Title format is "Traveler Briefing: <City>, <State> — <date>" — assert
        # on the stable City/State slug rather than the date portion.
        assert "Traveler Briefing: Los Angeles, CA" in data["title"]
        assert data["content"] == "## Local Digest\nTest local summary."
        assert db_session.query(Summary).count() == 1

        latest = test_client.get("/api/v1/summaries/latest/local?zip_code=90001")
        assert latest.status_code == 200
        latest_data = latest.json()
        assert latest_data["id"] == data["id"]
        assert latest_data["summary_type"] == "local"

    def test_generate_local_summary_not_found(self, test_client, monkeypatch):
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: None)

        resp = test_client.post("/api/v1/summaries/generate/local?zip_code=99999")
        assert resp.status_code == 404
        assert "Could not find location" in resp.json()["detail"]

    def test_latest_local_summary_returns_none_when_missing(self, test_client):
        resp = test_client.get("/api/v1/summaries/latest/local?zip_code=90001")
        assert resp.status_code == 200
        assert resp.json() is None

    def test_generate_local_summary_returns_cached_within_ttl(self, test_client, db_session, monkeypatch):
        """Revisiting the same ZIP within the cache TTL must return the existing
        Summary row without calling the LLM or inserting a duplicate.

        Why this matters: each LLM call costs 3-10s + tokens. Before caching, the
        dashboard regenerated on every app open, every location switch, and every
        revisit — burning latency and spend for content that hadn't changed.
        """
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))
        monkeypatch.setattr(
            "api.location._fetch_nws_alerts",
            lambda lat, lon, state: [_mock_local_alert("nws", "nws_001", "Local Severe Weather")],
        )
        monkeypatch.setattr(
            "api.location._fetch_airnow",
            lambda zip_code: [_mock_local_alert("airnow", f"{zip_code}_PM25_2026-04-10", "Local Air Quality")],
        )

        mock_return = ("## Local Digest\nTest local summary.", 42, "openai/gpt-5.2")
        with patch("llm.summarizer.Summarizer._call_llm", return_value=mock_return) as mock_llm:
            # First request: cache MISS → calls LLM + inserts row.
            first = test_client.post("/api/v1/summaries/generate/local?zip_code=90001")
            assert first.status_code == 200
            assert mock_llm.call_count == 1
            assert db_session.query(Summary).count() == 1

            # Second request (same ZIP, within TTL): cache HIT → no LLM call,
            # no new row, returns the existing summary.
            second = test_client.post("/api/v1/summaries/generate/local?zip_code=90001")
            assert second.status_code == 200
            assert mock_llm.call_count == 1, "LLM should not be called on cache hit"
            assert db_session.query(Summary).count() == 1, "Should not insert a duplicate summary"
            assert second.json()["id"] == first.json()["id"]

    def test_generate_local_summary_force_bypasses_cache(self, test_client, db_session, monkeypatch):
        """`force=true` must bypass the cache and regenerate, so pull-to-refresh
        or manual refresh can always get fresh LLM output."""
        monkeypatch.setattr("api.location._zip_to_coords", lambda zip_code: (34.05, -118.24, "Los Angeles", "CA"))
        monkeypatch.setattr(
            "api.location._fetch_nws_alerts",
            lambda lat, lon, state: [_mock_local_alert("nws", "nws_001", "Local Severe Weather")],
        )
        monkeypatch.setattr("api.location._fetch_airnow", lambda zip_code: [])

        mock_return = ("## Local Digest\nTest.", 42, "openai/gpt-5.2")
        with patch("llm.summarizer.Summarizer._call_llm", return_value=mock_return) as mock_llm:
            test_client.post("/api/v1/summaries/generate/local?zip_code=90001")
            test_client.post("/api/v1/summaries/generate/local?zip_code=90001&force=true")

            assert mock_llm.call_count == 2, "force=true should skip cache and call LLM again"
            assert db_session.query(Summary).count() == 2, "force=true should insert a new row"


class TestCallLlm:
    def test_resolve_model_falls_back_to_safe_default(self):
        from llm.summarizer import Summarizer

        with (
            patch("config.settings.settings.LLM_MODEL", ""),
            patch("config.settings.settings.LLM_MODEL_GUEST", ""),
            patch("config.settings.settings.LLM_MODEL_PREMIUM", ""),
        ):
            summarizer = Summarizer()
            assert summarizer._resolve_model() == "gpt-4o-mini"
            assert summarizer._resolve_model(is_premium=True) == "gpt-4o-mini"

    def test_call_llm_returns_text_and_tokens(self):
        from llm.summarizer import Summarizer

        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_usage = MagicMock()
        mock_usage.total_tokens = 42
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = mock_usage

        with (
            patch("config.settings.settings.OPENROUTER_API_KEY", "test-key"),
            patch("config.settings.settings.LLM_MODEL", "test-model"),
            patch("config.settings.settings.LLM_MODEL_GUEST", ""),
            patch("config.settings.settings.LLM_MODEL_PREMIUM", ""),
            patch("openai.OpenAI") as mock_client_cls,
        ):
            mock_client_cls.return_value.chat.completions.create.return_value = mock_completion
            summarizer = Summarizer()
            text, tokens, model = summarizer._call_llm("system prompt", "user prompt")

        assert text == "Test response"
        assert tokens == 42
        assert model == "test-model"

    def test_call_llm_raises_without_api_key(self):
        from llm.summarizer import Summarizer
        import pytest

        with patch("config.settings.settings.OPENROUTER_API_KEY", ""):
            summarizer = Summarizer()
            with pytest.raises(ValueError, match="No LLM API key configured"):
                summarizer._call_llm("system", "user")

    def test_call_llm_handles_null_usage(self):
        from llm.summarizer import Summarizer

        mock_message = MagicMock()
        mock_message.content = "Response without usage"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_completion.usage = None

        with (
            patch("config.settings.settings.OPENROUTER_API_KEY", "test-key"),
            patch("config.settings.settings.LLM_MODEL", "test-model"),
            patch("config.settings.settings.LLM_MODEL_GUEST", ""),
            patch("config.settings.settings.LLM_MODEL_PREMIUM", ""),
            patch("openai.OpenAI") as mock_client_cls,
        ):
            mock_client_cls.return_value.chat.completions.create.return_value = mock_completion
            summarizer = Summarizer()
            text, tokens, model = summarizer._call_llm("system", "user")

        assert text == "Response without usage"
        assert tokens == 0
        assert model == "test-model"
