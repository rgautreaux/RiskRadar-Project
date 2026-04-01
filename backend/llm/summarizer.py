"""LLM summarizer — generates daily digests and breaking alert summaries."""

import json
import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session
import openai

from config.settings import settings
from db.models import Alert, Summary
import llm.prompts as prompts


logger = logging.getLogger(__name__)


class Summarizer:
    def _resolve_model(self, is_premium: bool = False) -> str:
        """Return the LLM model name for the given user tier."""
        if is_premium and settings.LLM_MODEL_PREMIUM:
            return settings.LLM_MODEL_PREMIUM
        if not is_premium and settings.LLM_MODEL_GUEST:
            return settings.LLM_MODEL_GUEST
        return settings.LLM_MODEL

    def _call_llm(self, system: str, user: str, is_premium: bool = False) -> tuple[str, int, str]:
        """Call the configured LLM provider. Returns (text, token_count, model_used)."""
        if settings.OPENROUTER_API_KEY:
            model = self._resolve_model(is_premium)
            client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.OPENROUTER_API_KEY,
                )

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
        else:
            raise ValueError("No LLM API key configured")
        
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

        user_msg = prompts.TRIP_PACKING_USER.format(
            count=len(alerts),
            date=date.today().strftime("%B %d, %Y"),
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        text, tokens, model = self._call_llm(prompts.TRIP_PACKING_SYSTEM, user_msg, is_premium=is_premium)

        summary = Summary(
            title=f"Environmental Digest — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="daily",
            alert_ids=json.dumps([a.id for a in alerts]),
            region="US",
            model_used=model,
            token_count=tokens,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        logger.info(f"Daily digest generated: {len(alerts)} alerts, {tokens} tokens")
        return summary

    def generate_local_digest(
        self, db: Session, alerts: list, city: str, state: str, zip_code: str, is_premium: bool = False
    ) -> "Summary":
        """Generate a summary scoped to a specific location."""
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

        user_msg = prompts.TRIP_PACKING_USER.format(
            count=len(alerts),
            date=date.today().strftime("%B %d, %Y"),
            city=city,
            state=state,
            zip_code=zip_code,
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        text, tokens, model = self._call_llm(prompts.TRIP_PACKING_SYSTEM, user_msg, is_premium=is_premium)

        summary = Summary(
            title=f"Local Digest for {city}, {state} — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="local",
            alert_ids=json.dumps([a.id for a in alerts]),
            region=f"{city}, {state} {zip_code}",
            model_used=model,
            token_count=tokens,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        logger.info(f"Local digest for {city}, {state}: {len(alerts)} alerts, {tokens} tokens")
        return summary
