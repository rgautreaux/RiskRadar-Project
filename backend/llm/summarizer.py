"""LLM summarizer — generates daily digests and breaking alert summaries."""

import json
import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from config.settings import settings
from db.models import Alert, Summary
from llm.prompts import DAILY_DIGEST_SYSTEM, DAILY_DIGEST_USER, BREAKING_SYSTEM, BREAKING_USER

logger = logging.getLogger(__name__)


class Summarizer:
    def _call_llm(self, system: str, user: str) -> tuple[str, int]:
        """Call the configured LLM provider. Returns (text, token_count)."""
        if settings.LLM_PROVIDER == "openai":
            import openai

            client = openai.OpenAI(api_key=settings.LLM_API_KEY)
            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=2000,
            )
            text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens if resp.usage else 0
            return text, tokens

        elif settings.LLM_PROVIDER == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
            resp = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = resp.content[0].text
            tokens = resp.usage.input_tokens + resp.usage.output_tokens
            return text, tokens

        raise RuntimeError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")

    def generate_daily_digest(self, db: Session, since_hours: int = 24) -> Summary | None:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
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

        user_msg = DAILY_DIGEST_USER.format(
            count=len(alerts),
            date=date.today().strftime("%B %d, %Y"),
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        text, tokens = self._call_llm(DAILY_DIGEST_SYSTEM, user_msg)

        summary = Summary(
            title=f"Environmental Digest — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="daily",
            alert_ids=json.dumps([a.id for a in alerts]),
            region="US",
            model_used=settings.LLM_MODEL,
            token_count=tokens,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        logger.info(f"Daily digest generated: {len(alerts)} alerts, {tokens} tokens")
        return summary

    def generate_breaking_summary(self, alert: Alert) -> str:
        """Short summary for push notifications."""
        alert_data = {
            "type": alert.alert_type,
            "title": alert.title,
            "description": (alert.description or "")[:300],
            "location": alert.location_name,
            "severity": alert.severity,
        }
        user_msg = BREAKING_USER.format(alert_json=json.dumps(alert_data))
        text, _ = self._call_llm(BREAKING_SYSTEM, user_msg)
        return text
