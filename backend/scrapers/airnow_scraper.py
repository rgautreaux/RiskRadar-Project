"""AirNow — current air quality observations.

API docs: https://docs.airnowapi.org/CurrentObservationsByZip/docs
Requires an API key (free registration).
"""

import json
import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


def _aqi_to_severity(aqi: int) -> str:
    if aqi <= 50:
        return "low"
    if aqi <= 100:
        return "moderate"
    if aqi <= 200:
        return "high"
    return "critical"


class AirNowScraper(BaseScraper):
    source_name = "airnow"
    alert_type = "air_quality"

    def fetch_raw_data(self) -> list[dict]:
        url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
        params = {
            "format": "application/json",
            "zipCode": settings.DEFAULT_ZIP_CODE,
            "distance": 25,
            "API_KEY": settings.AIRNOW_API_KEY,
        }

        resp = httpx.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def normalize(self, raw: dict) -> dict:
        aqi = raw.get("AQI", 0)
        param = raw.get("ParameterName", "Unknown")
        date = raw.get("DateObserved", "").strip()
        area = raw.get("ReportingArea", "")
        state = raw.get("StateCode", "")
        category = raw.get("Category", {}).get("Name", "")

        return {
            "source": self.source_name,
            "source_id": f"{settings.DEFAULT_ZIP_CODE}_{param}_{date}",
            "alert_type": self.alert_type,
            "severity": _aqi_to_severity(aqi),
            "title": f"{param} AQI: {aqi} ({category})",
            "description": f"Air quality in {area}, {state}: {param} AQI is {aqi} ({category}). Observed {date}.",
            "raw_data": json.dumps(raw),
            "latitude": raw.get("Latitude"),
            "longitude": raw.get("Longitude"),
            "location_name": f"{area}, {state}",
            "event_start": date or None,
            "event_end": None,
        }
