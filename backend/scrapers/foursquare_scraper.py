"""FourSquare - collecting and integrating geospatial information.

API docs: https://docs.foursquare.com/developer/reference/foursquare-apis-overview
Console docs: https://docs.foursquare.com/developer/docs/developer-console-overview
Requires an API key (free registration).
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


class FourSquareScraper(BaseScraper):
    source_name = "foursquare"
    alert_type = "geospace"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.FESTIVALS_API_KEY:
            return []

        url = "https://docs.foursquare.com/developer/reference/foursquare-apis-overview/aq/observation/zipCode/current/"
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
