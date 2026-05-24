import json
from collections.abc import Iterable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import (
    Alert,
    AlertRawPayload,
    Location,
    Summary,
    SummaryAlert,
    User,
    UserAlertTypePreference,
    ZipGeo,
)

VALID_ALERT_TYPES = {"all", "weather", "air_quality", "wildfire", "pollution", "earthquake"}


def parse_legacy_json_array(raw_value: str | None, default: list[str] | None = None) -> list[str]:
    fallback = default[:] if default else []
    if not raw_value:
        return fallback
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return fallback
    if not isinstance(value, list):
        return fallback
    return [str(item) for item in value]


def get_user_alert_types(db: Session, user: User) -> list[str]:
    rows = (
        db.query(UserAlertTypePreference)
        .filter(UserAlertTypePreference.user_id == user.id)
        .all()
    )
    if rows:
        return [row.alert_type for row in rows]
    legacy = parse_legacy_json_array(user.alert_types, default=["all"])
    valid = [item for item in legacy if item in VALID_ALERT_TYPES]
    return valid or ["all"]


def set_user_alert_types(db: Session, user: User, alert_types: Iterable[str], dual_write_legacy: bool = True) -> list[str]:
    cleaned = [str(item) for item in alert_types if str(item) in VALID_ALERT_TYPES]
    if not cleaned:
        cleaned = ["all"]

    (
        db.query(UserAlertTypePreference)
        .filter(UserAlertTypePreference.user_id == user.id)
        .delete(synchronize_session=False)
    )
    for alert_type in cleaned:
        db.add(UserAlertTypePreference(user_id=user.id, alert_type=alert_type))

    if dual_write_legacy:
        user.alert_types = json.dumps(cleaned)

    return cleaned


def get_summary_alert_ids(db: Session, summary: Summary) -> list[int]:
    rows = (
        db.query(SummaryAlert)
        .filter(SummaryAlert.summary_id == summary.id)
        .all()
    )
    if rows:
        return [row.alert_id for row in rows]

    legacy = parse_legacy_json_array(summary.alert_ids, default=[])
    result: list[int] = []
    for item in legacy:
        try:
            result.append(int(item))
        except ValueError:
            continue
    return result


def set_summary_alert_ids(
    db: Session,
    summary: Summary,
    alert_ids: Iterable[int],
    dual_write_legacy: bool = True,
) -> list[int]:
    unique_ids = sorted({int(alert_id) for alert_id in alert_ids})

    (
        db.query(SummaryAlert)
        .filter(SummaryAlert.summary_id == summary.id)
        .delete(synchronize_session=False)
    )
    for alert_id in unique_ids:
        db.add(SummaryAlert(summary_id=summary.id, alert_id=alert_id))

    if dual_write_legacy:
        summary.alert_ids = json.dumps(unique_ids)

    return unique_ids


def ensure_alert_location(db: Session, alert: Alert) -> None:
    if alert.latitude is None or alert.longitude is None or not alert.location_name:
        return

    def _query_existing() -> Location | None:
        return (
            db.query(Location)
            .filter(
                Location.latitude == alert.latitude,
                Location.longitude == alert.longitude,
                Location.location_name == alert.location_name,
            )
            .first()
        )

    location = _query_existing()
    if location is None:
        try:
            # Use a savepoint so only the failed INSERT is rolled back,
            # not the entire outer transaction.
            with db.begin_nested():
                location = Location(
                    latitude=alert.latitude,
                    longitude=alert.longitude,
                    location_name=alert.location_name,
                )
                db.add(location)
                db.flush()  # execute INSERT so the DB assigns location.id
        except IntegrityError:
            # A concurrent alert in the same batch already inserted this row;
            # the savepoint was rolled back — re-query to get the existing one.
            location = _query_existing()
    if location is None:
        return
    alert.location_id = location.id


def ensure_alert_raw_payload(db: Session, alert: Alert) -> None:
    if alert.raw_data is None:
        return
    row = db.query(AlertRawPayload).filter(AlertRawPayload.alert_id == alert.id).first()
    if row is None:
        db.add(AlertRawPayload(alert_id=alert.id, raw_payload=alert.raw_data))
    else:
        row.raw_payload = alert.raw_data


def upsert_zip_geo(
    db: Session,
    zip_code: str,
    latitude: float,
    longitude: float,
    state: str | None = None,
    city: str | None = None,
) -> ZipGeo:
    row = db.query(ZipGeo).filter(ZipGeo.zip_code == zip_code).first()
    if row is None:
        row = ZipGeo(
            zip_code=zip_code,
            latitude=latitude,
            longitude=longitude,
            state=state,
            city=city,
        )
        db.add(row)
        return row

    row.latitude = latitude
    row.longitude = longitude
    if state is not None:
        row.state = state
    if city is not None:
        row.city = city
    return row


def get_effective_user_coords(db: Session, user: User) -> tuple[float | None, float | None]:
    if user.latitude is not None and user.longitude is not None:
        return user.latitude, user.longitude

    if user.zip_code:
        match = db.query(ZipGeo).filter(ZipGeo.zip_code == user.zip_code).first()
        if match:
            return match.latitude, match.longitude

    return None, None
