"""Allevents - integrating event information.

API docs: https://allevents.developer.azure-api.net/apis
Offers a free tier for developers to get started and prototype. The free access tier is for basic or limited use, with the scope not fully detailed and intended for prototyping, small-scale testing, or low-volume requests
"""

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


class AlleventsScraper(BaseScraper):
    source_name = "allevents"
    alert_type = "event"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.FESTIVALS_API_KEY:
            return []

        url = "https://www.allevents.developer.azure-api.net/aq/observation/zipCode/current/"
        params = {
            "format": "application/json",
            "zipCode": settings.DEFAULT_ZIP_CODE,
            "distance": 25,
            "API_KEY": settings.FESTIVALS_API_KEY,
        }

        resp = httpx.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()


    def normalize(self, raw: dict) -> dict:
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
            "description": f"There is an event in {area}, {state}: {param} The Event is {aqi} ({category}). Observed {date}.",
            "raw_data": raw,
            "latitude": raw.get("Latitude"),
            "longitude": raw.get("Longitude"),
            "location_name": f"{area}, {state}",
            "event_start": date or None,
            "event_end": None,
        }
