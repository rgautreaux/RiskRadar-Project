"""National Parks Service - provides data for national parks and protected areas users may find interest in

API docs: https://www.nps.gov/subjects/developer/api-documentation.htm
API site: https://www.nps.gov/subjects/developer/index.htm
This appears to be free to use!
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class NationalParksScraper(BaseScraper):
    source_name = "nps"
    alert_type = "location information"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.NPS_API_KEY:
            return []

        url = "https://api.nps.gov/api/v1/places/by-bbox"
        params = {
            "format": "application/json",
            "bbox": f"{settings.DEFAULT_LON_MIN},{settings.DEFAULT_LAT_MIN},{settings.DEFAULT_LON_MAX},{settings.DEFAULT_LAT_MAX}",
            "radius": 25,
            "api_key": settings.NPS_API_KEY,
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
