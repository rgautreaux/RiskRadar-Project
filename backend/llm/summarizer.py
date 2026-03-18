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
        if settings.LLM_PROVIDER in ("openai", "deepseek"):
            import openai

            # DeepSeek uses the OpenAI-compatible API with a different base URL
            if settings.LLM_PROVIDER == "deepseek":
                client = openai.OpenAI(
                    # api_key="sk-190105abaaf345c38ff6e75984afb6cc",
                    api_key=settings.LLM_API_KEY,
                    base_url="https://api.deepseek.com",
                )
            else:
                client = openai.OpenAI(api_key=settings.LLM_API_KEY)

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_completion_tokens=settings.LLM_MAX_TOKENS,
            )
            text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens if resp.usage else 0
            return text, tokens

        elif settings.LLM_PROVIDER == "anthropic":
            import anthropic

            #client = anthropic.Anthropic(api_key="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")
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

    def generate_local_digest(
        self, db: Session, alerts: list, city: str, state: str, zip_code: str
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

        user_msg = DAILY_DIGEST_USER.format(
            count=len(alerts),
            date=date.today().strftime("%B %d, %Y"),
            alerts_json=json.dumps(alerts_data, indent=2),
        )

        text, tokens = self._call_llm(DAILY_DIGEST_SYSTEM, user_msg)

        summary = Summary(
            title=f"Local Digest for {city}, {state} — {date.today().strftime('%b %d, %Y')}",
            content=text,
            summary_type="local",
            alert_ids=json.dumps([a.id for a in alerts]),
            region=f"{city}, {state} {zip_code}",
            model_used=settings.LLM_MODEL,
            token_count=tokens,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        logger.info(f"Local digest for {city}, {state}: {len(alerts)} alerts, {tokens} tokens")
        return summary
