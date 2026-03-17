"""NASA FIRMS - active fire / hotspot data.

API docs: https://firms.modaps.eosdis.nasa.gov/api/
Requires a MAP_KEY (free registration).
"""

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper


def _fire_severity(confidence: str, brightness: float) -> str:
    if confidence == "high" and brightness > 400:
        return "critical"
    if confidence == "high":
        return "high"
    if confidence == "nominal":
        return "moderate"
    return "low"


class FIRMSScraper(BaseScraper):
    source_name = "firms"
    alert_type = "wildfire"

    def fetch_raw_data(self) -> list[dict]:
        if not settings.NASA_FIRMS_MAP_KEY:
            raise RuntimeError("NASA_FIRMS_MAP_KEY not set")

        lat = settings.DEFAULT_LAT
        lon = settings.DEFAULT_LON
        # Bounding box: +-5 degrees around default location
        west = lon - 5
        south = lat - 5
        east = lon + 5
        north = lat + 5

        url = (
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{settings.NASA_FIRMS_MAP_KEY}/VIIRS_NOAA20_NRT/"
            f"{west},{south},{east},{north}/1"
        )

        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()

        # Parse CSV response
        lines = resp.text.strip().split("\n")
        if len(lines) < 2:
            return []

        headers = lines[0].split(",")
        results = []
        for line in lines[1:]:
            values = line.split(",")
            if len(values) == len(headers):
                results.append(dict(zip(headers, values)))
        return results

    def normalize(self, raw: dict) -> dict:
        lat = raw.get("latitude", "")
        lon = raw.get("longitude", "")
        brightness = float(raw.get("bright_ti4", 0) or 0)
        confidence = raw.get("confidence", "low").lower()
        acq_date = raw.get("acq_date", "")
        acq_time = raw.get("acq_time", "")

        return {
            "source": self.source_name,
            "source_id": f"firms_{lat}_{lon}_{acq_date}_{acq_time}",
            "alert_type": self.alert_type,
            "severity": _fire_severity(confidence, brightness),
            "title": f"Active Fire Detected ({confidence} confidence)",
            "description": (
                f"VIIRS satellite detected fire at ({lat}, {lon}) "
                f"on {acq_date} {acq_time}. Brightness: {brightness}K, "
                f"Confidence: {confidence}."
            ),
            "raw_data": raw,
            "latitude": float(lat) if lat else None,
            "longitude": float(lon) if lon else None,
            "location_name": f"({lat}, {lon})",
            "event_start": f"{acq_date}T{acq_time}" if acq_date else None,
            "event_end": None,
        }
