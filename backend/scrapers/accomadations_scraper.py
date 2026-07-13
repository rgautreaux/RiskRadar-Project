"""Accommodation API - provides access to a comprehensive dataset of accommodations, including hotels, guesthouses, and similar types of lodging


API docs: https://databrowser.opendatahub.com/dataset-overview/7c8f490d-7b54-4a88-801f-f7669f5aaed9?ref=freepublicapis.com
API Site: https://www.freepublicapis.com/accommodation-api
Unclear terms
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class AccommodationAPI(BaseScraper):
    source_name = "accommodation"
    alert_type = "lodging"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.ACCOMMODATION_API_KEY:
            return []

        url = "https://api.accommodation.com/accommodation-api/1.0/"
        params = {
            "bbox": f"{settings.DEFAULT_LON_MIN},{settings.DEFAULT_LAT_MIN},{settings.DEFAULT_LON_MAX},{settings.DEFAULT_LAT_MAX}",
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
