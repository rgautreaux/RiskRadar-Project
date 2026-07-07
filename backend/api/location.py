"""On-demand location-based data fetching.

When a user enters a zip code or city name, this module resolves it to
coordinates, fetches fresh alerts from NWS and AirNow, stores them in the DB,
and returns them.
"""

import re
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config.settings import settings
from db.database import get_db
from db.models import Alert
from schemas.alert import AlertOut

logger = logging.getLogger(__name__)

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
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        return None


# ── City name geocoding using Nominatim (OpenStreetMap) ──────────────

# US state abbreviation → full name mapping for parsing Nominatim results
_STATE_ABBREVS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC",
}


def _reverse_geocode_zip(lat: float, lon: float) -> str | None:
    """Reverse-geocode coordinates to find the nearest US zip code via Nominatim."""
    try:
        resp = httpx.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
            headers={"User-Agent": "RiskRadar/1.0 (school-project)"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        postcode = resp.json().get("address", {}).get("postcode")
        if postcode and len(postcode) >= 5 and postcode[:5].isdigit():
            return postcode[:5]
        return None
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        return None


_POPULATED_PLACE_TYPES = {"city", "town", "village", "hamlet", "suburb", "neighbourhood"}


def _city_to_coords(query: str) -> tuple[float, float, str, str, str | None] | None:
    """Geocode a city name to (lat, lon, city, state, zip_code) using Nominatim.

    Rejects results that resolve to administrative boundaries (states, counties)
    rather than populated places — a query like "Texas" should return None rather
    than a nonsensical {city: "Texas", state: "TX"} record.
    """
    try:
        resp = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "countrycodes": "us",
                "format": "json",
                "limit": 5,
                "addressdetails": 1,
            },
            headers={"User-Agent": "RiskRadar/1.0 (school-project)"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        results = resp.json()
        if not results:
            return None

        # Pick the first result that's a populated place (city/town/village),
        # not a state/county/region. Nominatim's addresstype tells us what kind
        # of place the top-level hit is.
        hit = None
        for r in results:
            addr_type = r.get("addresstype", "")
            r_addr = r.get("address", {})
            if addr_type in _POPULATED_PLACE_TYPES:
                hit = r
                break
            # Fallback: addresstype might be "administrative" but the address
            # block still contains a concrete city/town/village — accept those.
            if addr_type != "state" and addr_type != "country" and (
                r_addr.get("city") or r_addr.get("town") or r_addr.get("village")
            ):
                hit = r
                break
        if hit is None:
            return None

        lat = float(hit["lat"])
        lon = float(hit["lon"])

        addr = hit.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village") or query.split(",")[0].strip()
        state_full = addr.get("state", "")
        state = _STATE_ABBREVS.get(state_full, state_full[:2].upper() if state_full else "")

        # Extract zip code from address details (Nominatim often includes it)
        zip_code = addr.get("postcode")
        # Nominatim may return extended zip (e.g. "10001:10299"), take the first 5 digits
        if zip_code and len(zip_code) >= 5:
            zip_code = zip_code[:5] if zip_code[:5].isdigit() else None
        else:
            zip_code = None

        # Fallback: if forward search didn't include a postcode, reverse-geocode
        # the coordinates to find one (Nominatim reverse usually returns it).
        if not zip_code:
            zip_code = _reverse_geocode_zip(lat, lon)

        return lat, lon, city, state, zip_code
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        logger.exception("City geocoding failed for query: %s", query)
        return None


def _is_zip(q: str) -> bool:
    """Check if a query string looks like a US zip code."""
    return bool(re.match(r"^\d{5}$", q.strip()))


def _parse_state_intent(q: str) -> str | None:
    """Extract a 2-letter US state code from the 'state' portion of 'City, State'.

    Returns the 2-letter state code when the query explicitly names a state
    (either as a 2-letter abbreviation or an unambiguous prefix of a full
    state name). Returns None when the query has no comma, when the state
    portion is too short to disambiguate, or when the state isn't a valid US
    state.

    Examples:
        "Houston, TX"      -> "TX"
        "Houston, Texas"   -> "TX"
        "Houston, Tex"     -> "TX"   (unique prefix of Texas)
        "Houston, Te"      -> None   (ambiguous: Texas or Tennessee)
        "Houston"          -> None
        "Dallas, XX"       -> None   (not a real state)
    """
    if "," not in q:
        return None
    after = q.rsplit(",", 1)[1].strip()
    if len(after) == 0:
        return None

    # Exact 2-letter abbreviation
    if len(after) == 2 and after.isalpha():
        code = after.upper()
        return code if code in _STATE_ABBREVS.values() else None

    # Full-name prefix match, case-insensitive
    if len(after) >= 3:
        lowered = after.lower()
        matches = [
            code for full, code in _STATE_ABBREVS.items()
            if full.lower().startswith(lowered)
        ]
        # Only accept an unambiguous single match — typing "Te" could mean
        # Texas or Tennessee, so bail out rather than guess.
        if len(matches) == 1:
            return matches[0]
    return None


# ── NWS on-demand fetch ──────────────────────────────────────────────

SEVERITY_MAP = {
    "Extreme": "critical",
    "Severe": "high",
    "Moderate": "moderate",
    "Minor": "low",
    "Unknown": "moderate",
}


def _nws_get(url: str, params: dict, headers: dict, retries: int = 2) -> httpx.Response:
    """GET with automatic retry for transient NWS connection drops."""
    for attempt in range(retries + 1):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp
        except (httpx.RemoteProtocolError, httpx.ConnectError) as exc:
            if attempt < retries:
                logger.warning("NWS request failed (attempt %d/%d): %s", attempt + 1, retries + 1, exc)
                continue
            raise


def _fetch_nws_alerts(lat: float, lon: float, state: str) -> list[dict]:
    """Fetch active NWS weather alerts for a location."""
    url = "https://api.weather.gov/alerts/active"
    headers = {
        "User-Agent": "RiskRadar/1.0 (school-project)",
        "Accept": "application/geo+json",
    }

    # Try point-based first (NWS needs max 4 decimal places)
    resp = _nws_get(url, params={"point": f"{round(lat, 4)},{round(lon, 4)}"}, headers=headers)
    features = resp.json().get("features", [])

    # If none, try state-wide but cap to 25 to avoid flooding for large states
    if not features:
        resp2 = _nws_get(url, params={"area": state}, headers=headers)
        features = resp2.json().get("features", [])[:25]

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


def _airnow_observations(zip_code: str) -> list[dict]:
    """Fetch raw AirNow observations as scalar dicts.

    Returns a list of observations like:
        {aqi, parameter, category, area, state, date, latitude, longitude}

    Empty list when no API key is configured or the request fails.
    """
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
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError, ValueError, KeyError, IndexError, TypeError):
        return []

    observations = []
    for raw in raw_items:
        observations.append({
            "aqi": raw.get("AQI", 0),
            "parameter": raw.get("ParameterName", "Unknown"),
            "category": raw.get("Category", {}).get("Name", ""),
            "area": raw.get("ReportingArea", ""),
            "state": raw.get("StateCode", ""),
            "date": raw.get("DateObserved", "").strip(),
            "latitude": raw.get("Latitude"),
            "longitude": raw.get("Longitude"),
        })
    return observations


def _fetch_airnow(zip_code: str) -> list[dict]:
    """Fetch current air quality for a zip code from AirNow, shaped as alerts."""
    results = []
    for obs in _airnow_observations(zip_code):
        aqi = obs["aqi"]
        param = obs["parameter"]
        date = obs["date"]
        area = obs["area"]
        state = obs["state"]
        category = obs["category"]

        results.append({
            "source": "airnow",
            "source_id": f"{zip_code}_{param}_{date}",
            "alert_type": "air_quality",
            "severity": _aqi_to_severity(aqi),
            "title": f"{param} AQI: {aqi} ({category})",
            "description": f"Air quality in {area}, {state}: {param} AQI is {aqi} ({category}). Observed {date}.",
            "latitude": obs["latitude"],
            "longitude": obs["longitude"],
            "location_name": f"{area}, {state}",
            "event_start": date or None,
            "event_end": None,
        })
    return results


# ── Google Pollen API on-demand fetch ───────────────────────────────

_POLLEN_SEVERITY = {
    "None": "low",
    "Very Low": "low",
    "Low": "low",
    "Moderate": "moderate",
    "High": "high",
    "Very High": "critical",
}


def _pollen_observations(lat: float, lon: float) -> list[dict]:
    """Fetch raw pollen types from Google Pollen API as scalar dicts.

    Returns a list of in-season pollen types like:
        {name, category, value, description, date}

    Empty list when no API key is configured or the request fails.
    """
    api_key = settings.GOOGLE_POLLEN_API_KEY
    if not api_key:
        return []

    url = "https://pollen.googleapis.com/v1/forecast:lookup"
    params = {
        "key": api_key,
        "location.latitude": round(lat, 4),
        "location.longitude": round(lon, 4),
        "days": 1,
    }

    try:
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        logger.exception("Google Pollen API fetch failed for lat=%s lon=%s", lat, lon)
        return []

    observations = []
    for day_info in data.get("dailyInfo", []):
        date_obj = day_info.get("date", {})
        date_str = f"{date_obj.get('year', 1970)}-{date_obj.get('month', 1):02d}-{date_obj.get('day', 1):02d}" if date_obj else ""

        for pollen_type in day_info.get("pollenTypeInfo", []):
            if not pollen_type.get("inSeason"):
                continue

            index_info = pollen_type.get("indexInfo", {})
            observations.append({
                "name": pollen_type.get("displayName", "Pollen"),
                "category": index_info.get("category", "Unknown"),
                "value": index_info.get("value", 0),
                "description": index_info.get("indexDescription", ""),
                "date": date_str,
            })

    return observations


def _fetch_pollen(lat: float, lon: float) -> list[dict]:
    """Fetch pollen forecast from Google Pollen API, shaped as alerts."""
    results = []
    for obs in _pollen_observations(lat, lon):
        name = obs["name"]
        category = obs["category"]
        value = obs["value"]
        date_str = obs["date"]
        description_text = obs["description"]

        full_desc = f"{name} pollen: {category} (index {value}). {description_text}"

        results.append({
            "source": "google_pollen",
            "source_id": f"pollen_{name.lower()}_{date_str}_{round(lat, 2)}_{round(lon, 2)}",
            "alert_type": "pollen",
            "severity": _POLLEN_SEVERITY.get(category, "moderate"),
            "title": f"{name} Pollen: {category} ({value}/5)",
            "description": full_desc,
            "latitude": lat,
            "longitude": lon,
            "location_name": None,
            "event_start": date_str or None,
            "event_end": None,
        })

    return results


# ── Endpoint ─────────────────────────────────────────────────────────

@router.get("/alerts", response_model=list[AlertOut])
def get_alerts_for_location(
    zip_code: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    state: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Fetch fresh alerts from NWS and AirNow.
    Accepts either a zip_code OR lat+lon+state coordinates."""
    if zip_code:
        if len(zip_code) != 5 or not zip_code.isdigit():
            raise HTTPException(status_code=400, detail="Invalid zip code")
        location = _zip_to_coords(zip_code)
        if not location:
            raise HTTPException(status_code=404, detail=f"Could not find location for zip code {zip_code}")
        lat, lon, _city, state = location
    elif lat is not None and lon is not None and state:
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates: lat must be -90..90, lon must be -180..180")
    else:
        raise HTTPException(status_code=400, detail="Provide either zip_code or lat+lon+state")

    # Check for cached NWS/AirNow alerts near these coordinates (within ~50km box)
    ttl = settings.LOCATION_CACHE_TTL_MINUTES
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=ttl)
    cached_weather = (
        db.query(Alert)
        .filter(
            Alert.fetched_at >= cutoff,
            Alert.source.in_(["nws", "airnow"]),
            Alert.latitude.isnot(None),
            Alert.latitude.between(lat - 0.5, lat + 0.5),
            Alert.longitude.between(lon - 0.5, lon + 0.5),
        )
        .order_by(Alert.fetched_at.desc())
        .limit(limit)
        .all()
    )

    # Always fetch pollen (daily data, fast API, no rate-limit concern)
    pollen_alerts: list[dict] = []
    try:
        pollen_alerts = _fetch_pollen(lat, lon)
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        logger.exception("Google Pollen fetch failed for lat=%s lon=%s", lat, lon)

    # If we have fresh weather/AQ cache, combine with pollen and return
    if cached_weather:
        # Store any new pollen alerts in DB
        pollen_stored = []
        for alert_data in pollen_alerts:
            existing = (
                db.query(Alert)
                .filter_by(source=alert_data["source"], source_id=alert_data["source_id"])
                .first()
            )
            if existing:
                pollen_stored.append(existing)
            else:
                alert = Alert(**alert_data)
                db.add(alert)
                pollen_stored.append(alert)
        if pollen_alerts:
            try:
                db.commit()
                for a in pollen_stored:
                    db.refresh(a)
            except IntegrityError:
                db.rollback()
                pollen_stored = []
                for alert_data in pollen_alerts:
                    existing = db.query(Alert).filter_by(
                        source=alert_data["source"], source_id=alert_data["source_id"]
                    ).first()
                    if existing:
                        pollen_stored.append(existing)
        return list(cached_weather) + pollen_stored

    # No fresh cache — fetch from external APIs (graceful on failure)
    all_alerts: list[dict] = []
    try:
        all_alerts.extend(_fetch_nws_alerts(lat, lon, state))
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        logger.exception("NWS alert fetch failed for lat=%s lon=%s", lat, lon)
    if zip_code:
        try:
            all_alerts.extend(_fetch_airnow(zip_code))
        except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
            logger.exception("AirNow fetch failed for zip=%s", zip_code)
    all_alerts.extend(pollen_alerts)

    # Deduplicate by (source, source_id) before touching the session to avoid
    # autoflush IntegrityErrors when the same alert appears more than once in
    # the combined fetch results.
    seen_keys: dict[tuple[str, str], dict] = {}
    for alert_data in all_alerts:
        key = (alert_data["source"], alert_data["source_id"])
        seen_keys[key] = alert_data
    all_alerts = list(seen_keys.values())

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

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Re-fetch all matching alerts in one query instead of per-item lookups
        stored = (
            db.query(Alert)
            .filter(
                Alert.fetched_at >= cutoff,
                Alert.source.in_(["nws", "airnow"]),
                Alert.latitude.isnot(None),
                Alert.latitude.between(lat - 0.5, lat + 0.5),
                Alert.longitude.between(lon - 0.5, lon + 0.5),
            )
            .order_by(Alert.fetched_at.desc())
            .all()
        )

    # Refresh to get IDs
    for a in stored:
        db.refresh(a)

    return stored[:limit]


@router.get("/search")
def search_location(q: str = Query(..., min_length=2, description="City name or 5-digit zip code")):
    """Unified search: accepts a city name (e.g. 'Houston, TX') or a zip code (e.g. '70506').
    Returns city, state, coordinates, and zip_code (if known)."""
    q = q.strip()

    if _is_zip(q):
        location = _zip_to_coords(q)
        if not location:
            raise HTTPException(status_code=404, detail=f"Could not find location for zip code {q}")
        lat, lon, city, state = location
        return {"city": city, "state": state, "zip_code": q, "latitude": lat, "longitude": lon}

    # City name search
    location = _city_to_coords(q)
    if not location:
        raise HTTPException(status_code=404, detail=f"Could not find location for '{q}'")
    lat, lon, city, state, zip_code = location
    return {"city": city, "state": state, "zip_code": zip_code, "latitude": lat, "longitude": lon}


@router.get("/autocomplete")
def autocomplete_location(q: str = Query(..., min_length=2, description="Partial city name")):
    """Return up to 5 city suggestions for typeahead search.

    Respects an explicit state in the query. Typing "Houston, Texas" will
    filter out Houston, MO — because the user has already committed to a
    state. Typing "Houston" or "Houston, Te" (ambiguous state prefix) will
    not filter. Also skips non-populated-place hits (counties, states).
    """
    if _is_zip(q):
        # No autocomplete for zip codes
        return []

    intent_state = _parse_state_intent(q)

    try:
        resp = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q,
                "countrycodes": "us",
                "format": "json",
                "limit": 10,  # Fetch extra — we may filter down
                "addressdetails": 1,
            },
            headers={"User-Agent": settings.NWS_USER_AGENT},
            timeout=5,
        )
        if resp.status_code != 200:
            return []

        results = []
        for hit in resp.json():
            addr = hit.get("address", {})
            addr_type = hit.get("addresstype", "")
            city = addr.get("city") or addr.get("town") or addr.get("village")
            if not city:
                continue
            # Skip non-populated-place hits like states, counties, regions
            if addr_type not in _POPULATED_PLACE_TYPES and addr_type not in ("", "administrative"):
                continue
            state_full = addr.get("state", "")
            state = _STATE_ABBREVS.get(state_full, state_full[:2].upper() if state_full else "")
            # Honor explicit state intent — drop mismatched states
            if intent_state and state != intent_state:
                continue
            label = f"{city}, {state}" if state else city
            # Avoid duplicate labels
            if not any(r["label"] == label for r in results):
                results.append({"label": label, "city": city, "state": state})
            if len(results) >= 5:
                break

        return results
    except (httpx.RequestError, ValueError, KeyError, IndexError, TypeError):
        return []


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


# ── Lightweight scalar endpoints for dashboard widgets ──────────────

@router.get("/aqi")
def get_air_quality(zip_code: str):
    """Return the current worst-case air quality reading for a zip code.

    Picks the single highest-AQI pollutant from AirNow's current observations
    (AirNow returns one row per pollutant — PM2.5, Ozone, etc.).
    """
    if len(zip_code) != 5 or not zip_code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid zip code")

    if not settings.AIRNOW_API_KEY:
        raise HTTPException(status_code=503, detail="Air quality data unavailable")

    observations = _airnow_observations(zip_code)
    if not observations:
        raise HTTPException(status_code=404, detail=f"No air quality data for zip code {zip_code}")

    worst = max(observations, key=lambda o: o.get("aqi", 0))
    return {
        "aqi": worst["aqi"],
        "category": worst["category"],
        "pollutant": worst["parameter"],
        "observed_at": worst["date"],
        "area": f"{worst['area']}, {worst['state']}".strip(", "),
    }


@router.get("/pollen")
def get_pollen(zip_code: str):
    """Return the current pollen reading for a zip code.

    Looks up coordinates from the zip, calls Google Pollen API, and returns
    an overall severity (max across in-season types) plus per-type breakdown.
    """
    if len(zip_code) != 5 or not zip_code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid zip code")

    if not settings.GOOGLE_POLLEN_API_KEY:
        raise HTTPException(status_code=503, detail="Pollen data unavailable")

    location = _zip_to_coords(zip_code)
    if not location:
        raise HTTPException(status_code=404, detail=f"Could not find location for zip code {zip_code}")

    lat, lon, _city, _state = location
    observations = _pollen_observations(lat, lon)
    if not observations:
        raise HTTPException(status_code=404, detail=f"No pollen data for zip code {zip_code}")

    # Overall = the type with the highest numeric value (Google uses 0–5 scale)
    overall_obs = max(observations, key=lambda o: o.get("value", 0))

    return {
        "overall": overall_obs["category"],
        "overall_value": overall_obs["value"],
        "types": [
            {
                "name": o["name"],
                "category": o["category"],
                "value": o["value"],
            }
            for o in observations
        ],
        "observed_at": overall_obs["date"],
    }
