"""LLM summarizer — generates daily digests and breaking alert summaries."""

import json
import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session
import openai

from config.settings import settings
from db.models import Alert, Summary
"""LLM summarizer — generates daily digests and breaking alert summaries."""

import json
import logging
from datetime import date, datetime, timedelta, timezone

import openai
from sqlalchemy.orm import Session

from config.settings import settings
from db.models import Alert, Summary
from db.normalization import ensure_alert_location, ensure_alert_raw_payload, set_summary_alert_ids
import llm.prompts as prompts


logger = logging.getLogger(__name__)


class Summarizer:
    def _build_fallback_summary(self, alerts_count: int, scope: str) -> str:
        """Return a deterministic plain-text briefing when the LLM is unavailable."""
        if alerts_count == 0:
            return (
                f"Low risk. No active alerts for {scope} today. Conditions look "
                "suitable for typical outdoor travel plans."
            )
        return (
            f"Moderate risk. {alerts_count} active alert(s) are in effect for {scope}. "
            "Our briefing service is temporarily unavailable — open the Alerts tab for "
            "the individual notices while we retry."
        )

    def _resolve_model(self, is_premium: bool = False) -> str:
        """Return the LLM model name for the given user tier."""
        explicit = getattr(settings, "LLM_MODEL", "").strip()
        if explicit:
            return explicit

        guest_model = (settings.LLM_MODEL_GUEST or "").strip() or "gpt-4o-mini"
        premium_model = (settings.LLM_MODEL_PREMIUM or "").strip() or guest_model
        return premium_model if is_premium else guest_model

    def _call_llm(self, system: str, user: str, is_premium: bool = False) -> tuple[str, int, str]:
        """Call the configured LLM provider. Returns (text, token_count, model_used)."""
        api_key = settings.OPENROUTER_API_KEY.strip() or settings.LLM_API_KEY.strip()

        if not api_key:
            raise ValueError("No LLM API key configured")

        model = self._resolve_model(is_premium)
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        text = completion.choices[0].message.content
        tokens = completion.usage.total_tokens if completion.usage else 0
        return text, tokens, model

    def generate_daily_digest(self, db: Session, since_hours: int = 24, is_premium: bool = False) -> Summary | None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        alerts = db.query(Alert).filter(Alert.fetched_at >= cutoff).all()

        if not alerts:
            return None

        alerts_data = [
            {
                "type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "description": (a.description or "")[:500],
                "location": a.location_name,
                "time": a.event_start,
            }
            for a in alerts
        ]

        user_msg = prompts.NATIONWIDE_BRIEFING_USER.format(
            count=len(alerts),
            date=date.today().strftime("%B %d, %Y"),
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        try:
            text, tokens, model = self._call_llm(
                prompts.TRAVELER_BRIEFING_SYSTEM,
                user_msg,
                is_premium=is_premium,
            )
        except (
            openai.APIConnectionError,
            openai.APIStatusError,
            openai.RateLimitError,
            openai.AuthenticationError,
            openai.BadRequestError,
            RuntimeError,
            ValueError,
            KeyError,
            AttributeError,
            IndexError,
        ) as exc:
            logger.warning("LLM daily digest fallback activated: %s", exc)
            text = self._build_fallback_summary(len(alerts), "the US")
            tokens = 0
            model = "fallback-no-llm"

        summary = Summary(
            title=f"Traveler Briefing — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="daily",
            alert_ids=json.dumps([a.id for a in alerts]) if settings.NORMALIZATION_DUAL_WRITE_LEGACY_JSON else None,
            region="US",
            model_used=model,
            token_count=tokens,
        )
        db.add(summary)
        db.flush()
        set_summary_alert_ids(
            db,
            summary,
            [a.id for a in alerts],
            dual_write_legacy=settings.NORMALIZATION_DUAL_WRITE_LEGACY_JSON,
        )
        for alert in alerts:
            ensure_alert_location(db, alert)
            ensure_alert_raw_payload(db, alert)
        db.commit()
        db.refresh(summary)
        logger.info("Daily digest generated: %s alerts, %s tokens", len(alerts), tokens)
        return summary

    def generate_local_digest(
        self, db: Session, alerts: list, city: str, state: str, zip_code: str, is_premium: bool = False
    ) -> "Summary":
        """Generate a travel-focused summary scoped to a specific location."""
        alerts_data = [
            {
                "type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "description": (a.description or "")[:500],
                "location": a.location_name,
                "time": a.event_start,
            }
            for a in alerts
        ]

        user_msg = prompts.TRAVELER_BRIEFING_USER.format(
            count=len(alerts),
            city=city,
            state=state,
            date=date.today().strftime("%B %d, %Y"),
            zip_code=zip_code,
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        try:
            text, tokens, model = self._call_llm(
                prompts.TRAVELER_BRIEFING_SYSTEM,
                user_msg,
                is_premium=is_premium,
            )
        except (
            openai.APIConnectionError,
            openai.APIStatusError,
            openai.RateLimitError,
            openai.AuthenticationError,
            openai.BadRequestError,
            ValueError,
            KeyError,
            AttributeError,
            IndexError,
        ) as exc:
            logger.warning("LLM local digest fallback activated for %s, %s: %s", city, state, exc)
            text = self._build_fallback_summary(len(alerts), f"{city}, {state}")
            tokens = 0
            model = "fallback-no-llm"

        summary = Summary(
            title=f"Traveler Briefing: {city}, {state} — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="local",
            alert_ids=json.dumps([a.id for a in alerts]) if settings.NORMALIZATION_DUAL_WRITE_LEGACY_JSON else None,
            region=f"{city}, {state} {zip_code}",
            model_used=model,
            token_count=tokens,
        )
        db.add(summary)
        db.flush()
        set_summary_alert_ids(
            db,
            summary,
            [a.id for a in alerts],
            dual_write_legacy=settings.NORMALIZATION_DUAL_WRITE_LEGACY_JSON,
        )
        for alert in alerts:
            ensure_alert_location(db, alert)
            ensure_alert_raw_payload(db, alert)
        db.commit()
        db.refresh(summary)
        logger.info("Local digest for %s, %s: %s alerts, %s tokens", city, state, len(alerts), tokens)
        return summary
