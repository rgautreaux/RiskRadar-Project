"""EPA Envirofacts - Toxics Release Inventory (TRI) facility data.

API docs: https://www.epa.gov/enviro/envirofacts-data-service-api
No API key required.
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class EPAScraper(BaseScraper):
    source_name = "epa"
    alert_type = "pollution"

    def fetch_raw_data(self) -> list[dict]:
        # Query TRI facilities in California (default state)
        url = "https://data.epa.gov/efservice/tri_facility/state_abbr/CA/rows/0:24/JSON"

        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def normalize(self, raw: dict) -> dict:
        tri_id = raw.get("tri_facility_id", "")
        name = raw.get("facility_name", "Unknown Facility")
        city = raw.get("city_name", "")
        state = raw.get("state_abbr", "")
        county = raw.get("county_name", "")
        lat = raw.get("pref_latitude")
        lon = raw.get("pref_longitude")

        return {
            "source": self.source_name,
            "source_id": f"epa_{tri_id}",
            "alert_type": self.alert_type,
            "severity": "moderate",
            "title": f"TRI Facility: {name}",
            "description": f"EPA-tracked toxic release facility: {name} in {city}, {county} County, {state}.",
            "raw_data": raw,
            "latitude": float(lat) if lat else None,
            "longitude": float(lon) if lon else None,
            "location_name": f"{city}, {state}" if city else state,
            "event_start": None,
            "event_end": None,
        }
