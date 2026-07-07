import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models import Alert, User, ZipGeo
from db.normalization import get_user_alert_types
from config.settings import settings
from auth.security import get_current_user_optional
from schemas.alert import AlertOut, AlertStats

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# Simple zip-code prefix to approximate lat/lon lookup.
# This covers major regions; a full dataset would use a geocoding API.
_ZIP_COORDS: dict[str, tuple[float, float]] = {
    "700": (30.0, -90.2),   # Louisiana (New Orleans area)
    "701": (30.2, -92.0),   # Louisiana (Lafayette area)
    "703": (30.5, -91.2),   # Louisiana (Baton Rouge area)
    "704": (32.5, -93.7),   # Louisiana (Shreveport area)
    "705": (30.2, -92.0),   # Louisiana (Lafayette/Lake Charles)
    "706": (31.3, -92.4),   # Louisiana (Alexandria)
    "707": (29.9, -90.1),   # Louisiana (New Orleans)
    "708": (30.2, -93.2),   # Louisiana (Lake Charles)
    "750": (32.8, -96.8),   # Texas (Dallas)
    "770": (29.8, -95.4),   # Texas (Houston)
    "900": (34.1, -118.2),  # California (Los Angeles)
    "910": (34.1, -118.2),  # California (Los Angeles area)
    "920": (32.7, -117.2),  # California (San Diego)
    "940": (37.8, -122.4),  # California (San Francisco)
    "950": (37.3, -121.9),  # California (San Jose)
    "100": (40.7, -74.0),   # New York
    "200": (38.9, -77.0),   # DC area
    "300": (33.7, -84.4),   # Georgia (Atlanta)
    "330": (25.8, -80.2),   # Florida (Miami)
    "606": (41.9, -87.6),   # Illinois (Chicago)
}


def _zip_to_coords(zip_code: str) -> tuple[float, float] | None:
    """Convert a 5-digit zip code to approximate (lat, lon) using prefix lookup."""
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in _ZIP_COORDS:
            return _ZIP_COORDS[prefix]
    return None


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in miles between two lat/lon points."""
    R = 3959  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Map state abbreviations to full names for location_name matching
_STATE_FROM_ZIP_PREFIX: dict[str, str] = {
    "700": "LA", "701": "LA", "703": "LA", "704": "LA",
    "705": "LA", "706": "LA", "707": "LA", "708": "LA",
    "750": "TX", "770": "TX",
    "900": "CA", "910": "CA", "920": "CA", "940": "CA", "950": "CA",
    "100": "NY", "200": "DC", "300": "GA", "330": "FL", "606": "IL",
}


def _zip_to_state(zip_code: str) -> str | None:
    """Get state abbreviation from zip code prefix."""
    for prefix_len in (3, 2, 1):
        prefix = zip_code[:prefix_len]
        if prefix in _STATE_FROM_ZIP_PREFIX:
            return _STATE_FROM_ZIP_PREFIX[prefix]
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
    valid_alert_types = {"weather", "air_quality", "wildfire", "pollution", "earthquake", "pollen"}
    valid_severity = {"low", "moderate", "high", "critical"}

    if alert_type and alert_type not in valid_alert_types:
        raise HTTPException(status_code=422, detail="Invalid alert_type")

    if severity and severity not in valid_severity:
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
        elif state:
            # No coords in lookup, but we know the state — filter by name
            q = q.filter(
                Alert.location_name.isnot(None),
                Alert.location_name.like(f"%, {state}%"),
            )

    return q.order_by(Alert.fetched_at.desc()).offset(offset).limit(limit).all()


@router.get("/stats", response_model=AlertStats)
def alert_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Alert.id)).scalar()

    by_type = dict(
        db.query(Alert.alert_type, func.count(Alert.id))
        .group_by(Alert.alert_type)
        .all()
    )
    by_severity = dict(
        db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )

    return AlertStats(total=total or 0, by_type=by_type, by_severity=by_severity)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
