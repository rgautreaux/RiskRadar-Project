"""HBX Group - Hotel BookingAPI is the main hotel API in the HBX Group API ecosystem. It covers the complete booking process; it is designed to book hotels in real-time as fast as in two steps and 
allows to generate lists of hotels, confirm bookings, get lists of bookings, manage cancellations & modifications and obtain booking information.


API docs: https://developer.hotelbeds.com/documentation/getting-started/
API Site: https://developer.hotelbeds.com/
Free to use once api key is aquired
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class HotelBedsAPI(BaseScraper):
    source_name = "hotelbeds"
    alert_type = "lodging"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.HOTELBEDS_API_KEY:
            return []

        url = "https://api.hotelbeds.com/hotel-api/1.0/"
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
