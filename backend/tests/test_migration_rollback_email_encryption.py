from db.migrations import rollback_email_encryption as rollback
from db.models import MigrationLog, User


def test_rollback_emails_restores_plaintext_and_clears_encrypted_fields(db_session, monkeypatch):
    user = User(
        display_name="Encrypted",
        email=None,
        email_encrypted="enc:value",
        email_hmac="hmac:value",
        password_hash="x",
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    monkeypatch.setattr(rollback, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(rollback, "decrypt_email", lambda value: "restored@test.com")

    code = rollback.rollback_emails(dry_run=False)

    updated = db_session.query(User).filter(User.id == user_id).one()
    assert code == 0
    assert updated.email == "restored@test.com"
    assert updated.email_encrypted is None
    assert updated.email_hmac is None

    logs = db_session.query(MigrationLog).order_by(MigrationLog.id.asc()).all()
    assert any(log.action == "email_encryption_rollback_batch" and log.status == "started" for log in logs)
    assert any(log.action == "email_encryption_rollback" and log.status == "success" and log.user_id == user_id for log in logs)
    assert any(log.action == "email_encryption_rollback_batch" and log.status == "completed" for log in logs)


def test_rollback_emails_dry_run_does_not_mutate_user_rows(db_session, monkeypatch):
    user = User(
        display_name="Encrypted",
        email=None,
        email_encrypted="enc:value",
        email_hmac="hmac:value",
        password_hash="x",
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    monkeypatch.setattr(rollback, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(rollback, "decrypt_email", lambda value: "restored@test.com")

    code = rollback.rollback_emails(dry_run=True)

    updated = db_session.query(User).filter(User.id == user_id).one()
    assert code == 0
    assert updated.email is None
    assert updated.email_encrypted == "enc:value"
    assert updated.email_hmac == "hmac:value"

    completed = (
        db_session.query(MigrationLog)
        .filter(
            MigrationLog.action == "email_encryption_rollback_batch",
            MigrationLog.status == "completed",
        )
        .order_by(MigrationLog.id.desc())
        .first()
    )
    assert completed is not None
    assert "dry_run=1" in (completed.error_message or "")
