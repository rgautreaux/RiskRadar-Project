import logging
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models import Alert, User, ZipGeo
from db.normalization import get_user_alert_types
from config.settings import settings
from auth.security import get_current_user_optional
from schemas.alert import AlertOut, AlertStats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _zip_to_coords(zip_code: str) -> tuple[float, float, str | None] | None:
    """Convert a 5-digit zip code to (lat, lon, state) using the zippopotam.us API.

    Reuses the same free API that location.py uses, so any valid US zip code
    is supported instead of a small hardcoded prefix table.
    """
    try:
        import httpx
        resp = httpx.get(f"https://api.zippopotam.us/us/{zip_code}", timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        place = data["places"][0]
        lat = float(place["latitude"])
        lon = float(place["longitude"])
        state = place["state abbreviation"]
        return lat, lon, state
    except Exception:
        logger.debug("Zip lookup failed for %s", zip_code)
        return None


@router.get("", response_model=list[AlertOut])
def list_alerts(
    alert_type: str | None = None,
    severity: str | None = None,
    source: str | None = None,
    zip_code: str | None = Query(default=None, min_length=5, max_length=5, pattern=r"^\d{5}$"),
    radius_miles: float = Query(default=150, le=500),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    valid_alert_types = {"weather", "air_quality", "wildfire", "pollution", "earthquake"}
    valid_severity = {"low", "moderate", "high", "critical"}

    if alert_type and alert_type not in valid_alert_types:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid alert_type")

    if severity and severity not in valid_severity:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Invalid severity")

    q = db.query(Alert)
    has_explicit_filters = any([alert_type, severity, source, zip_code])

    if current_user and not has_explicit_filters:
        if not alert_type:
            preferred_types = get_user_alert_types(db, current_user)
            if "all" not in preferred_types:
                filtered_types = [item for item in preferred_types if item in valid_alert_types]
                if filtered_types:
                    q = q.filter(Alert.alert_type.in_(filtered_types))

        if not severity and current_user.notify_severity in valid_severity:
            severity_windows = {
                "low": ["low", "moderate", "high", "critical"],
                "moderate": ["moderate", "high", "critical"],
                "high": ["high", "critical"],
                "critical": ["critical"],
            }
            q = q.filter(Alert.severity.in_(severity_windows[current_user.notify_severity]))

    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    if severity:
        q = q.filter(Alert.severity == severity)
    if source:
        q = q.filter(Alert.source == source)

    if zip_code and len(zip_code) == 5:
<<<<<<< HEAD
        coords = None
        if settings.GEO_USE_ZIP_LOOKUP:
            zip_match = db.query(ZipGeo).filter(ZipGeo.zip_code == zip_code).first()
            if zip_match:
                coords = (zip_match.latitude, zip_match.longitude)
        if coords is None:
            coords = _zip_to_coords(zip_code)
        state = _zip_to_state(zip_code)
        if coords:
            lat, lon = coords
            # Filter by bounding box first (rough filter), then haversine
=======
        result = _zip_to_coords(zip_code)
        if result:
            lat, lon, state = result
            # Filter by bounding box first (rough filter)
>>>>>>> QuiV2
            deg_offset = radius_miles / 55  # ~55 miles per degree
            q = q.filter(
                (
                    (Alert.latitude.isnot(None)) &
                    (Alert.latitude >= lat - deg_offset) &
                    (Alert.latitude <= lat + deg_offset) &
                    (Alert.longitude >= lon - deg_offset) &
                    (Alert.longitude <= lon + deg_offset)
                ) | (
                    # Also match by state in location_name for alerts without coords
                    (Alert.latitude.is_(None)) &
                    (Alert.location_name.isnot(None)) &
                    (Alert.location_name.like(f"%, {state}%"))
                )
            )
        # If zip lookup failed, return unfiltered results rather than silently
        # dropping the zip filter — the caller can see from the results that
        # the zip wasn't resolved.

    return q.order_by(Alert.fetched_at.desc()).offset(offset).limit(limit).all()


@router.get("/stats", response_model=AlertStats)
def alert_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Alert.id)).scalar() or 0

    by_type = {
        k: v for k, v in db.query(Alert.alert_type, func.count(Alert.id))
        .group_by(Alert.alert_type).all()
        if k is not None
    }
    by_severity = {
        k: v for k, v in db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity).all()
        if k is not None
    }

    return AlertStats(total=total, by_type=by_type, by_severity=by_severity)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
