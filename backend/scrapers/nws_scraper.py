"""NOAA National Weather Service - active weather alerts.

API docs: https://www.weather.gov/documentation/services-web-api
No API key required, but a User-Agent header is mandatory.
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper

SEVERITY_MAP = {
    "Extreme": "critical",
    "Severe": "high",
    "Moderate": "moderate",
    "Minor": "low",
    "Unknown": "moderate",
}


class NWSScraper(BaseScraper):
    source_name = "nws"
    alert_type = "weather"

    def fetch_raw_data(self) -> list[dict]:
        url = "https://api.weather.gov/alerts/active"
        headers = {"User-Agent": settings.NWS_USER_AGENT, "Accept": "application/geo+json"}

        # First try point-based query for the exact location
        params = {"point": f"{settings.DEFAULT_LAT},{settings.DEFAULT_LON}"}
        resp = httpx.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])

        # If no alerts for exact point, broaden to the forecast zone
        if not features:
            try:
                point_url = f"https://api.weather.gov/points/{settings.DEFAULT_LAT},{settings.DEFAULT_LON}"
                point_resp = httpx.get(point_url, headers=headers, timeout=30)
                point_resp.raise_for_status()
                zone_url = point_resp.json().get("properties", {}).get("forecastZone", "")
                if zone_url:
                    zone_id = zone_url.rsplit("/", 1)[-1]  # e.g. "CAZ368"
                    state = zone_id[:2]  # e.g. "CA"
                    resp2 = httpx.get(url, params={"area": state}, headers=headers, timeout=30)
                    resp2.raise_for_status()
                    features = resp2.json().get("features", [])
            except Exception:
                pass  # Fall back to empty list if zone lookup fails

        return features

    def normalize(self, raw: dict) -> dict:
        props = raw.get("properties", {})
        geometry = raw.get("geometry")

        lat, lon = None, None
        if geometry and geometry.get("coordinates"):
            coords = geometry["coordinates"]
            # GeoJSON polygon — take centroid of first ring
            if geometry["type"] == "Polygon":
                ring = coords[0]
                lon = sum(c[0] for c in ring) / len(ring)
                lat = sum(c[1] for c in ring) / len(ring)
            elif geometry["type"] == "Point":
                lon, lat = coords[0], coords[1]

        return {
            "source": self.source_name,
            "source_id": props.get("id", ""),
            "alert_type": self.alert_type,
            "severity": SEVERITY_MAP.get(props.get("severity", "Unknown"), "moderate"),
            "title": props.get("headline", props.get("event", "Weather Alert")),
            "description": props.get("description", ""),
            "raw_data": props,
            "latitude": lat,
            "longitude": lon,
            "location_name": props.get("areaDesc", ""),
            "event_start": props.get("onset"),
            "event_end": props.get("expires"),
        }
