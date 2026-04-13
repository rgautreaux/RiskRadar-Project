import json
from importlib import import_module

from db.models import Alert, Summary, User
from tests.conftest import NOW

backfill_summaries = import_module("db.migrations.backfill_summary_alerts")
backfill_user_types = import_module("db.migrations.backfill_user_alert_type_preferences")
validate_summaries = import_module("db.migrations.parity_validator_summaries_alerts")
validate_user_types = import_module("db.migrations.parity_validator_user_alert_types")


def test_summary_backfill_and_parity_validator(db_session, monkeypatch):
    alert = Alert(
        source="nws",
        source_id="nws_002",
        alert_type="weather",
        severity="high",
        title="Storm",
        fetched_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(alert)
    db_session.commit()

    summary = Summary(
        title="Digest",
        content="text",
        summary_type="daily",
        alert_ids=json.dumps([alert.id]),
        generated_at=NOW,
        created_at=NOW,
    )
    db_session.add(summary)
    db_session.commit()

    monkeypatch.setattr(backfill_summaries, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(validate_summaries, "SessionLocal", lambda: db_session)

    assert backfill_summaries.run_backfill(batch_size=10) == 0
    assert validate_summaries.run_validator() == 0


def test_user_alert_type_backfill_and_parity_validator(db_session, monkeypatch):
    user = User(
        display_name="Prefs",
        email="prefs@test.com",
        password_hash="x",
        alert_types=json.dumps(["weather", "wildfire"]),
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(backfill_user_types, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(validate_user_types, "SessionLocal", lambda: db_session)

    assert backfill_user_types.run_backfill(batch_size=10) == 0
    assert validate_user_types.run_validator() == 0
