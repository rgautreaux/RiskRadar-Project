from datetime import datetime, timezone

from sqlalchemy import text

from db.migrations import preflight as migration_preflight
from db.models import NotificationDispatchLog, User

NOW = datetime.now(timezone.utc)


def test_preflight_passes_on_clean_database(db_session, monkeypatch):
    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 0


def test_preflight_strict_blocks_plaintext_email_rows(db_session, monkeypatch):
    user = User(
        display_name="Legacy User",
        email="legacy@example.com",
        password_hash="hash",
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight(strict=True)

    assert code == 2


def test_preflight_blocks_orphan_notification_dispatch_rows(db_session, monkeypatch):
    dispatch_log = NotificationDispatchLog(
        alert_id=999,
        initiated_by_user_id=999,
        provider="noop",
        recipients_total=0,
        sent_count=0,
        failed_count=0,
        status="success",
        created_at=NOW,
    )
    db_session.add(dispatch_log)
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2


def test_preflight_blocks_missing_required_index(db_session, monkeypatch):
    db_session.execute(text("DROP INDEX idx_alerts_source_fetched_at"))
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2