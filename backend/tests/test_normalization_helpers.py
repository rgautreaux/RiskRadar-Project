import json

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
from db.normalization import (
    ensure_alert_location,
    ensure_alert_raw_payload,
    get_effective_user_coords,
    get_summary_alert_ids,
    get_user_alert_types,
    set_summary_alert_ids,
    set_user_alert_types,
)
from tests.conftest import NOW


def test_set_and_get_user_alert_types_relational(db_session):
    user = User(display_name="A", email="a@test.com", password_hash="x", created_at=NOW, updated_at=NOW)
    db_session.add(user)
    db_session.commit()

    set_user_alert_types(db_session, user, ["weather", "earthquake"], dual_write_legacy=True)
    db_session.commit()

    rows = db_session.query(UserAlertTypePreference).filter(UserAlertTypePreference.user_id == user.id).all()
    assert {row.alert_type for row in rows} == {"weather", "earthquake"}
    assert json.loads(user.alert_types) == ["weather", "earthquake"]
    assert set(get_user_alert_types(db_session, user)) == {"weather", "earthquake"}


def test_set_and_get_summary_alert_ids_relational(db_session):
    alert = Alert(
        source="nws",
        source_id="nws_001",
        alert_type="weather",
        severity="high",
        title="Storm",
        fetched_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )
    summary = Summary(
        title="Digest",
        content="x",
        summary_type="daily",
        generated_at=NOW,
        created_at=NOW,
    )
    db_session.add_all([alert, summary])
    db_session.commit()

    set_summary_alert_ids(db_session, summary, [alert.id], dual_write_legacy=True)
    db_session.commit()

    rows = db_session.query(SummaryAlert).filter(SummaryAlert.summary_id == summary.id).all()
    assert [row.alert_id for row in rows] == [alert.id]
    assert json.loads(summary.alert_ids) == [alert.id]
    assert get_summary_alert_ids(db_session, summary) == [alert.id]


def test_ensure_alert_location_and_raw_payload(db_session):
    alert = Alert(
        source="epa",
        source_id="epa_001",
        alert_type="pollution",
        severity="moderate",
        title="AQI",
        raw_data={"aqi": 72},
        latitude=34.05,
        longitude=-118.24,
        location_name="Los Angeles, CA",
        fetched_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(alert)
    db_session.commit()

    ensure_alert_location(db_session, alert)
    ensure_alert_raw_payload(db_session, alert)
    db_session.commit()

    location = db_session.query(Location).filter(Location.id == alert.location_id).first()
    payload = db_session.query(AlertRawPayload).filter(AlertRawPayload.alert_id == alert.id).first()

    assert location is not None
    assert location.location_name == "Los Angeles, CA"
    assert payload is not None
    assert payload.raw_payload == {"aqi": 72}


def test_get_effective_user_coords_prefers_override_then_zip_lookup(db_session):
    user = User(display_name="Coords", email="coords@test.com", password_hash="x", zip_code="90001", created_at=NOW, updated_at=NOW)
    db_session.add(user)
    db_session.add(ZipGeo(zip_code="90001", latitude=34.1, longitude=-118.2, state="CA", city="Los Angeles"))
    db_session.commit()

    lat, lon = get_effective_user_coords(db_session, user)
    assert (lat, lon) == (34.1, -118.2)

    user.latitude = 40.0
    user.longitude = -73.0
    db_session.commit()

    lat, lon = get_effective_user_coords(db_session, user)
    assert (lat, lon) == (40.0, -73.0)
