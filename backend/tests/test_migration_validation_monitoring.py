from db.migrations import monitor_migration_log as monitor
from db.migrations import validate_email_migration as validator
from db.models import MigrationLog, User


def test_validation_success_when_all_emails_migrated(db_session, monkeypatch):
    user = User(
        display_name="Valid",
        email=None,
        email_encrypted="enc:value",
        email_hmac="hmac:value",
        password_hash="x",
    )
    db_session.add(user)
    db_session.add(
        MigrationLog(
            action="email_encryption_batch",
            status="completed",
            error_message="processed=1,succeeded=1,failed=0",
        )
    )
    db_session.commit()

    monkeypatch.setattr(validator, "SessionLocal", lambda: db_session)
    assert validator.run_validation() == 0


def test_validation_fails_when_plaintext_email_remains(db_session, monkeypatch):
    user = User(
        display_name="Legacy",
        email="legacy@test.com",
        password_hash="x",
    )
    db_session.add(user)
    db_session.add(MigrationLog(action="email_encryption_batch", status="completed"))
    db_session.commit()

    monkeypatch.setattr(validator, "SessionLocal", lambda: db_session)
    assert validator.run_validation() == 2


def test_monitor_alerts_when_threshold_reached(db_session, monkeypatch):
    db_session.add(MigrationLog(action="email_encryption_batch", status="started"))
    db_session.commit()
    db_session.add(
        MigrationLog(
            action="email_encryption",
            status="error",
            user_id=1,
            error_message="sanitized failure",
        )
    )
    db_session.commit()

    monkeypatch.setattr(monitor, "SessionLocal", lambda: db_session)
    monkeypatch.setenv("MIGRATION_ERROR_THRESHOLD", "1")
    assert monitor.run_monitoring() == 2


def test_monitor_ok_when_below_threshold(db_session, monkeypatch):
    db_session.add(
        MigrationLog(
            action="email_encryption",
            status="success",
            user_id=1,
        )
    )
    db_session.commit()

    monkeypatch.setattr(monitor, "SessionLocal", lambda: db_session)
    monkeypatch.setenv("MIGRATION_ERROR_THRESHOLD", "2")
    assert monitor.run_monitoring() == 0
