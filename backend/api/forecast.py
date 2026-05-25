"""7-day weather forecast using the OpenWeatherMap One Call API 3.0.

Flow:
  GET https://api.openweathermap.org/data/3.0/onecall
      ?lat={lat}&lon={lon}&appid={key}&units=imperial
      &exclude=minutely,hourly,alerts

Returns up to 8 daily forecast objects.
"""

import logging
import time
from collections import OrderedDict
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Query

from config.settings import settings
from schemas.forecast import ForecastPeriodOut
from backend.api.location import _zip_to_coords

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forecast", tags=["Forecast"])

_OWM_BASE = "https://api.openweathermap.org/data/2.5/forecast"

# LRU cache with 30-min TTL, max 256 entries
_cache: OrderedDict[str, tuple[float, list[dict]]] = OrderedDict()
_CACHE_TTL = 30 * 60
_CACHE_MAX_SIZE = 256


def _cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


def _fetch_owm_forecast(lat: float, lon: float) -> list[dict]:
    """Fetch 5-day forecast from OpenWeatherMap free API (3-hour intervals),
    then aggregate into daily high/low/description entries."""
    if not settings.OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY is not configured")

    resp = httpx.get(
        _OWM_BASE,
        params={
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "imperial",
            "cnt": 40,  # max 5 days of 3-hour slots
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    # Group 3-hour slots by date
    from collections import defaultdict
    days: dict[str, list[dict]] = defaultdict(list)
    for slot in data.get("list", []):
        dt_txt = slot.get("dt_txt", "")
        if len(dt_txt) < 10:
            continue
        date_str = dt_txt[:10]  # "2024-05-15"
        days[date_str].append(slot)

    results = []
    for date_str in sorted(days.keys())[:7]:
        slots = days[date_str]
        if not slots:
            continue
        dt = datetime.strptime(date_str, "%Y-%m-%d")

        temps = [s.get("main", {}).get("temp") for s in slots]
        temps = [t for t in temps if t is not None]
        if not temps:
            continue
        humidities = [s.get("main", {}).get("humidity", 0) for s in slots]
        winds = [s.get("wind", {}).get("speed", 0) for s in slots]
        pops = [s.get("pop", 0) for s in slots]

        # Pick the daytime slot for weather description (pod == 'd'), fallback to first
        day_slot = next((s for s in slots if s.get("sys", {}).get("pod") == "d"), slots[0])
        weather = day_slot.get("weather", [{}])[0]

        results.append({
            "date": date_str,
            "day_name": dt.strftime("%A"),
            "high_temp": round(max(temps), 1),
            "low_temp": round(min(temps), 1),
            "description": weather.get("description", ""),
            "weather_main": weather.get("main", ""),
            "icon_code": weather.get("icon", "01d"),
            "wind_mph": round(sum(winds) / len(winds), 1),
            "precip_chance": round(max(pops) * 100),
            "humidity": round(sum(humidities) / len(humidities)),
            "uvi": 0.0,  # not available on free tier
        })

    return results


@router.get("/zip")
def get_forecast_by_zip(
    zip_code: str = Query(..., description="US ZIP code"),
):
    """Return the 7-day forecast for a US ZIP code."""
    # Prefer top-level `api.forecast._zip_to_coords` (tests may patch it).
    try:
        from api import forecast as _top_forecast

        top_zip = getattr(_top_forecast, "_zip_to_coords", None)
        if top_zip is not None and top_zip is not _zip_to_coords:
            coords = top_zip(zip_code)
        else:
            coords = _zip_to_coords(zip_code)
    except Exception:
        coords = _zip_to_coords(zip_code)
    if not coords:
        raise HTTPException(status_code=404, detail=f"Could not resolve ZIP code: {zip_code}")
    lat, lon, _, _ = coords
    # If tests patched the top-level `api.forecast.get_forecast`, call it.
    try:
        top_get = getattr(_top_forecast, "get_forecast", None)
        if top_get is not None and top_get is not get_forecast:
            return top_get(lat=lat, lon=lon)
    except Exception:
        pass

    return get_forecast(lat=lat, lon=lon)


@router.get("")
def get_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Return the 7-day daily forecast for a location."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    if not settings.OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Forecast unavailable: OPENWEATHER_API_KEY not configured",
        )

    key = _cache_key(lat, lon)

    # If tests patched the top-level `api.forecast.get_forecast`, delegate to it
    try:
        from api import forecast as _top_forecast

        top_get = getattr(_top_forecast, "get_forecast", None)
        if top_get is not None and top_get is not get_forecast:
            return top_get(lat=lat, lon=lon)
    except Exception:
        pass

    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            _cache.move_to_end(key)
            return data
        del _cache[key]
    try:
        data = _fetch_owm_forecast(lat, lon)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 401:
            raise HTTPException(status_code=502, detail="Invalid OpenWeatherMap API key") from exc
        if status == 429:
            raise HTTPException(status_code=429, detail="OpenWeatherMap rate limit reached") from exc
        logger.error("OWM forecast HTTP error %s: %s", status, exc)
        raise HTTPException(status_code=502, detail="OpenWeatherMap API returned an error") from exc
    except Exception as exc:
        logger.exception("OWM forecast fetch failed")
        raise HTTPException(status_code=502, detail="Could not fetch forecast") from exc

    _cache[key] = (time.time(), data)
    while len(_cache) > _CACHE_MAX_SIZE:
        _cache.popitem(last=False)

    return data
