"""Migration Script: Encrypt and HMAC Existing User Emails.

This script migrates all users in the database:
- Encrypts the plaintext email into email_encrypted
- Computes HMAC for email_hmac
- Sets legacy email field to None (for privacy)
- Logs batch start/end and per-user actions to MigrationLog

Run this script in a safe environment after backing up the database.
"""

from datetime import datetime, timezone
from importlib import import_module
import os
import re
import sys
from pathlib import Path
from typing import cast

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

security_module = import_module("auth.security")
database_module = import_module("db.database")
models_module = import_module("db.models")

encrypt_email = security_module.encrypt_email
email_hmac = security_module.email_hmac
SessionLocal = database_module.SessionLocal
MigrationLog = models_module.MigrationLog
User = models_module.User


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_ERROR_LENGTH = 500
BATCH_SIZE = int(os.getenv("MIGRATION_BATCH_SIZE", "100"))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def safe_error_message(exc: Exception) -> str:
    """Sanitize exception text to avoid leaking sensitive values into logs."""
    message = str(exc) if exc else "unknown error"
    message = EMAIL_RE.sub("[REDACTED_EMAIL]", message)
    if len(message) > MAX_ERROR_LENGTH:
        return f"{message[:MAX_ERROR_LENGTH]}..."
    return message


def _log(
    db: Session,
    *,
    action: str,
    status: str,
    user_id: int | None = None,
    error_message: str | None = None,
) -> None:
    db.add(
        MigrationLog(
            timestamp=_now_utc(),
            user_id=user_id,
            action=action,
            status=status,
            error_message=error_message,
        )
    )


def _ensure_phase3_schema(db: Session) -> None:
    """Ensure only Phase 3 prerequisites exist before migrating data."""
    bind = db.get_bind()
    MigrationLog.__table__.create(bind=bind, checkfirst=True)

    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = [
        column_name for column_name in ("email_encrypted", "email_hmac") if column_name not in user_columns
    ]
    if missing_columns:
        raise RuntimeError(
            "Phase 3 schema prerequisites missing on users table "
            f"({', '.join(missing_columns)}). "
            "Apply backend/db/migrations/2026-04-10_phase3_email_security_schema.sql first."
        )

    has_unique_email_hmac = any(
        index.get("unique") and index.get("column_names") == ["email_hmac"]
        for index in inspector.get_indexes("users")
    ) or any(
        unique.get("column_names") == ["email_hmac"]
        for unique in inspector.get_unique_constraints("users")
    )
    if not has_unique_email_hmac:
        raise RuntimeError(
            "Phase 3 schema prerequisite missing: unique key on users.email_hmac. "
            "Apply backend/db/migrations/2026-04-10_phase3_email_security_schema.sql first."
        )

    db.commit()


def migrate_emails() -> int:
    db: Session = SessionLocal()
    processed = 0
    succeeded = 0
    failed = 0

    try:
        _ensure_phase3_schema(db)

        _log(db, action="email_encryption_batch", status="started")
        db.commit()

        last_id = 0
        while True:
            batch = (
                db.query(User)
                .filter(User.email.isnot(None), User.id > last_id)
                .order_by(User.id.asc())
                .limit(BATCH_SIZE)
                .all()
            )
            if not batch:
                break

            for user in batch:
                processed += 1
                user_id = cast(int, user.id)
                try:
                    with db.begin_nested():
                        original_email = cast(str | None, user.email)
                        if original_email is None or original_email == "":
                            raise ValueError("User email is empty")

                        setattr(user, "email_encrypted", encrypt_email(original_email))
                        setattr(user, "email_hmac", email_hmac(original_email))
                        setattr(user, "email", None)

                        _log(db, action="email_encryption", status="success", user_id=user_id)
                    succeeded += 1
                except (ValueError, TypeError, OSError, RuntimeError, SQLAlchemyError) as exc:
                    failed += 1
                    _log(
                        db,
                        action="email_encryption",
                        status="error",
                        user_id=user_id,
                        error_message=safe_error_message(exc),
                    )

            db.commit()
            last_id = batch[-1].id
            if len(batch) < BATCH_SIZE:
                break

        summary = f"processed={processed},succeeded={succeeded},failed={failed}"
        _log(db, action="email_encryption_batch", status="completed", error_message=summary)
        db.commit()
        return 0 if failed == 0 else 2
    except (ValueError, TypeError, OSError, RuntimeError, SQLAlchemyError) as exc:
        db.rollback()
        _log(
            db,
            action="email_encryption_batch",
            status="failed",
            error_message=safe_error_message(exc),
        )
        db.commit()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    code = migrate_emails()
    print("Migration complete." if code == 0 else "Migration finished with errors.")
    sys.exit(code)
