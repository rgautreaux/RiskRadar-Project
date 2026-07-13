"""Metriport -  intefrates Metriport's health content to help provide evidence-based health information with people who need it most to make informed choices and keep themselves safe

API docs: https://docs.metriport.com/medical-api/getting-started/quickstart
API site: https://www.metriport.com/
Open Source once an API Key is obtained
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class MetriportScraper(BaseScraper):
    source_name = "metriport"
    alert_type = "health"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.METRIPORT_API_KEY:
            return []

        url = "https://api.ucr.cjis.gov/metriport-api"
        params = {
            "format": "application/json",
            "bbox": f"{settings.DEFAULT_LON_MIN},{settings.DEFAULT_LAT_MIN},{settings.DEFAULT_LON_MAX},{settings.DEFAULT_LAT_MAX}",
            "radius": 25,
            "api_key": settings.METRIPORT_API_KEY,
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
