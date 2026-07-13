"""National Crime Victimization Survey (NCVS) - collects information on nonfatal personal crimes and household property crimes both reported and not reported to the police.

API docs: https://api.ojp.gov/bjsdataset/v1/gcuy-rt5g.csv?$limit=200000
API Site: https://bjs.ojp.gov/national-crime-victimization-survey-ncvs-api#1-0
Unclear on usage terms as of now
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


class NCVSScraper(BaseScraper):
    source_name = "ncvs"
    alert_type = "crime"

    def fetch_raw_data(self) -> list[dict]:
        # If API key not configured, avoid making external HTTP calls during tests
        if not settings.NCVS_API_KEY:
            return []

        url = "https://api.bjs.ojp.gov/national-crime-victimization-survey-ncvs-api"
        params = {
            "format": "application/json",
            "bbox": f"{settings.DEFAULT_LON_MIN},{settings.DEFAULT_LAT_MIN},{settings.DEFAULT_LON_MAX},{settings.DEFAULT_LAT_MAX}",
            "radius": 25,
            "api_key": settings.NCVS_API_KEY,
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
