from db.migrations import migrate_email_encryption as migration
from db.models import MigrationLog, User


def test_migrate_emails_success(db_session, monkeypatch):
    user = User(display_name="A", email="a@test.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    monkeypatch.setattr(migration, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(migration, "encrypt_email", lambda value: f"enc:{value}")
    monkeypatch.setattr(migration, "email_hmac", lambda value: f"hmac:{value}")

    code = migration.migrate_emails()

    updated = db_session.query(User).filter(User.id == user_id).one()
    assert code == 0
    assert updated.email is None
    assert updated.email_encrypted == "enc:a@test.com"
    assert updated.email_hmac == "hmac:a@test.com"

    logs = db_session.query(MigrationLog).order_by(MigrationLog.id.asc()).all()
    assert any(log.action == "email_encryption_batch" and log.status == "started" for log in logs)
    assert any(log.action == "email_encryption" and log.status == "success" and log.user_id == user_id for log in logs)
    assert any(log.action == "email_encryption_batch" and log.status == "completed" for log in logs)


def test_safe_error_message_redacts_email():
    exc = RuntimeError("duplicate email a@test.com caused conflict")
    safe = migration.safe_error_message(exc)
    assert "a@test.com" not in safe
    assert "[REDACTED_EMAIL]" in safe
