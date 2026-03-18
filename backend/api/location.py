"""On-demand location-based data fetching.

When a user enters a zip code, this endpoint fetches fresh alerts
from NWS and AirNow for that specific location, stores them in the DB,
and returns them.
"""

import math
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Alert
from schemas.alert import AlertOut

router = APIRouter(prefix="/location", tags=["Location"])


# ── Zip-to-coordinates lookup using a free API ──────────────────────

def _zip_to_coords(zip_code: str) -> tuple[float, float, str, str] | None:
    """Convert zip code to (lat, lon, city, state) using the zippopotam.us API."""
    try:
        resp = httpx.get(f"https://api.zippopotam.us/us/{zip_code}", timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        place = data["places"][0]
        lat = float(place["latitude"])
        lon = float(place["longitude"])
        city = place["place name"]
        state = place["state abbreviation"]
        return lat, lon, city, state
    except Exception:
        return None


# ── NWS on-demand fetch ──────────────────────────────────────────────

SEVERITY_MAP = {
    "Extreme": "critical",
    "Severe": "high",
    "Moderate": "moderate",
    "Minor": "low",
    "Unknown": "moderate",
}


def _fetch_nws_alerts(lat: float, lon: float, state: str) -> list[dict]:
    """Fetch active NWS weather alerts for a location."""
    url = "https://api.weather.gov/alerts/active"
    headers = {
        "User-Agent": "RiskRadar/1.0 (school-project)",
        "Accept": "application/geo+json",
    }

    # Try point-based first
    resp = httpx.get(url, params={"point": f"{lat},{lon}"}, headers=headers, timeout=30)
    resp.raise_for_status()
    features = resp.json().get("features", [])

    # If none, try state-wide
    if not features:
        resp2 = httpx.get(url, params={"area": state}, headers=headers, timeout=30)
        resp2.raise_for_status()
        features = resp2.json().get("features", [])

    results = []
    for raw in features:
        props = raw.get("properties", {})
        geometry = raw.get("geometry")
        alert_lat, alert_lon = None, None
        if geometry and geometry.get("coordinates"):
            coords = geometry["coordinates"]
            if geometry["type"] == "Polygon":
                ring = coords[0]
                alert_lon = sum(c[0] for c in ring) / len(ring)
                alert_lat = sum(c[1] for c in ring) / len(ring)
            elif geometry["type"] == "Point":
                alert_lon, alert_lat = coords[0], coords[1]

        results.append({
            "source": "nws",
            "source_id": props.get("id", ""),
            "alert_type": "weather",
            "severity": SEVERITY_MAP.get(props.get("severity", "Unknown"), "moderate"),
            "title": props.get("headline", props.get("event", "Weather Alert")),
            "description": props.get("description", ""),
            "latitude": alert_lat,
            "longitude": alert_lon,
            "location_name": props.get("areaDesc", ""),
            "event_start": props.get("onset"),
            "event_end": props.get("expires"),
        })
    return results


# ── AirNow on-demand fetch ───────────────────────────────────────────

def _aqi_to_severity(aqi: int) -> str:
    if aqi <= 50:
        return "low"
    if aqi <= 100:
        return "moderate"
    if aqi <= 200:
        return "high"
    return "critical"


def _fetch_airnow(zip_code: str) -> list[dict]:
    """Fetch current air quality for a zip code from AirNow."""
    from config.settings import settings
    api_key = settings.AIRNOW_API_KEY
    if not api_key:
        return []

    url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
    params = {
        "format": "application/json",
        "zipCode": zip_code,
        "distance": 50,
        "API_KEY": api_key,
    }

    try:
        resp = httpx.get(url, params=params, timeout=30)
        resp.raise_for_status()
        raw_items = resp.json()
    except Exception:
        return []

    results = []
    for raw in raw_items:
        aqi = raw.get("AQI", 0)
        param = raw.get("ParameterName", "Unknown")
        date = raw.get("DateObserved", "").strip()
        area = raw.get("ReportingArea", "")
        state = raw.get("StateCode", "")
        category = raw.get("Category", {}).get("Name", "")

        results.append({
            "source": "airnow",
            "source_id": f"{zip_code}_{param}_{date}",
            "alert_type": "air_quality",
            "severity": _aqi_to_severity(aqi),
            "title": f"{param} AQI: {aqi} ({category})",
            "description": f"Air quality in {area}, {state}: {param} AQI is {aqi} ({category}). Observed {date}.",
            "latitude": raw.get("Latitude"),
            "longitude": raw.get("Longitude"),
            "location_name": f"{area}, {state}",
            "event_start": date or None,
            "event_end": None,
        })
    return results


# ── Endpoint ─────────────────────────────────────────────────────────

@router.get("/alerts", response_model=list[AlertOut])
def get_alerts_for_location(
    zip_code: str,
    db: Session = Depends(get_db),
):
    """Fetch fresh alerts for a specific zip code from NWS and AirNow,
    store them in the database, and return them."""
    if len(zip_code) != 5 or not zip_code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid zip code")

    location = _zip_to_coords(zip_code)
    if not location:
        raise HTTPException(status_code=404, detail=f"Could not find location for zip code {zip_code}")

    lat, lon, city, state = location

    # Fetch from external APIs
    all_alerts: list[dict] = []
    all_alerts.extend(_fetch_nws_alerts(lat, lon, state))
    all_alerts.extend(_fetch_airnow(zip_code))

    # Store in DB (dedup by source + source_id)
    stored = []
    for alert_data in all_alerts:
        existing = (
            db.query(Alert)
            .filter_by(source=alert_data["source"], source_id=alert_data["source_id"])
            .first()
        )
        if existing:
            stored.append(existing)
        else:
            alert = Alert(**alert_data)
            db.add(alert)
            stored.append(alert)

    db.commit()
    # Refresh to get IDs
    for a in stored:
        db.refresh(a)

    return stored


@router.get("/info")
def get_location_info(zip_code: str):
    """Return city, state, and coordinates for a zip code."""
    if len(zip_code) != 5 or not zip_code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid zip code")

    location = _zip_to_coords(zip_code)
    if not location:
        raise HTTPException(status_code=404, detail=f"Could not find location for zip code {zip_code}")

    lat, lon, city, state = location
    return {"zip_code": zip_code, "city": city, "state": state, "latitude": lat, "longitude": lon}
