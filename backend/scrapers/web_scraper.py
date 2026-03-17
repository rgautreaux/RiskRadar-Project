"""Firecrawl + LLM web scraper.

Scrapes arbitrary websites using Firecrawl for content extraction,
then uses the configured LLM to extract structured alert data.
"""

import json
import logging
from typing import Any

from config.settings import settings
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """\
You are a structured data extractor for the RiskRadar environmental alert system.
Given the text content of a web page, extract environmental risk alerts as a JSON array.

Each alert must be a JSON object with exactly these fields:
- source_id (string): a unique identifier for this alert (construct from title + location if no ID exists)
- title (string): short descriptive title
- description (string): 1-2 sentence summary
- severity (string): one of "critical", "high", "moderate", "low"
- latitude (number or null): if location coordinates are available
- longitude (number or null): if location coordinates are available
- location_name (string): human-readable location
- event_start (string or null): ISO date/datetime if available
- event_end (string or null): ISO date/datetime if available

Return ONLY a JSON array. No markdown fences, no commentary.
If no relevant alerts are found, return an empty array: []"""

EXTRACTION_USER_PROMPT = """\
Source: {source_name}
Alert type: {alert_type}
{extraction_hints}

--- PAGE CONTENT ---
{page_content}
--- END ---

Extract all relevant alerts as a JSON array."""


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class WebScraper(BaseScraper):
    """A single instance handles one web_sources config entry."""

    def __init__(self, config: dict):
        self._config = config
        self.source_name = config["name"]
        self.alert_type = config["alert_type"]

    def fetch_raw_data(self) -> list[dict]:
        from firecrawl import FirecrawlApp

        firecrawl = FirecrawlApp(api_key="fc-fa26117bfd0f47f184cbe7add944d79f")

        scrape_params = {"formats": ["markdown"]}
        fc_options = self._config.get("firecrawl_options", {})
        if fc_options.get("wait_for"):
            scrape_params["waitFor"] = fc_options["wait_for"]
        if fc_options.get("only_main_content") is not None:
            scrape_params["onlyMainContent"] = fc_options["only_main_content"]

        result = firecrawl.scrape_url(self._config["url"], params=scrape_params)
        page_content = result.get("markdown", "") or result.get("content", "")

        if not page_content:
            logger.warning(f"[{self.source_name}] Firecrawl returned no content")
            return []

        # Truncate to avoid blowing LLM context limits
        max_chars = 12000
        if len(page_content) > max_chars:
            page_content = page_content[:max_chars] + "\n... [truncated]"

        hints_text = ""
        if self._config.get("extraction_hints"):
            hints_text = f"Extraction hints:\n{self._config['extraction_hints']}"

        user_msg = EXTRACTION_USER_PROMPT.format(
            source_name=self.source_name,
            alert_type=self.alert_type,
            extraction_hints=hints_text,
            page_content=page_content,
        )

        raw_json_str = self._call_llm(EXTRACTION_SYSTEM_PROMPT, user_msg)

        try:
            cleaned = raw_json_str.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            alerts = json.loads(cleaned)
            if not isinstance(alerts, list):
                alerts = [alerts]
            return alerts
        except json.JSONDecodeError as e:
            logger.error(f"[{self.source_name}] LLM returned invalid JSON: {e}")
            return []

    def _call_llm(self, system: str, user: str) -> str:
        """Call the configured LLM provider."""
        if settings.LLM_PROVIDER in ("openai", "deepseek"):
            import openai

            if settings.LLM_PROVIDER == "deepseek":
                client = openai.OpenAI(
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
                max_tokens=4000,
                temperature=0.1,
            )
            return resp.choices[0].message.content

        elif settings.LLM_PROVIDER == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
            resp = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=4000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return resp.content[0].text

        raise RuntimeError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")

    def normalize(self, raw: dict) -> dict:
        """LLM already returns structured data, so normalization is light."""
        return {
            "source": self.source_name,
            "source_id": str(raw.get("source_id", "")),
            "alert_type": self.alert_type,
            "severity": raw.get("severity", "moderate"),
            "title": raw.get("title", f"{self.source_name} alert"),
            "description": raw.get("description", ""),
            "raw_data": raw,
            "latitude": _safe_float(raw.get("latitude")),
            "longitude": _safe_float(raw.get("longitude")),
            "location_name": raw.get("location_name", ""),
            "event_start": raw.get("event_start"),
            "event_end": raw.get("event_end"),
        }
