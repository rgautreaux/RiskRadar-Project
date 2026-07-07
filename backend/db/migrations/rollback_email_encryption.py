"""Rollback utility for email encryption migration in staging/local environments.

This script restores plaintext email values from email_encrypted to support controlled
rollback drills. It is intended for staging validation and requires the same key
material used during encryption.
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

decrypt_email = security_module.decrypt_email
SessionLocal = database_module.SessionLocal
MigrationLog = models_module.MigrationLog
User = models_module.User

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_ERROR_LENGTH = 500
BATCH_SIZE = int(os.getenv("MIGRATION_BATCH_SIZE", "100"))
DRY_RUN = os.getenv("ROLLBACK_DRY_RUN", "false").lower() in {"1", "true", "yes"}


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


def _ensure_rollback_schema(db: Session) -> None:
    """Validate required rollback columns exist before processing rows."""
    bind = db.get_bind()
    MigrationLog.__table__.create(bind=bind, checkfirst=True)

    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = [
        column_name for column_name in ("email", "email_encrypted", "email_hmac") if column_name not in user_columns
    ]
    if missing_columns:
        raise RuntimeError(
            "Rollback prerequisites missing on users table "
            f"({', '.join(missing_columns)}). "
            "Apply required schema migrations before running rollback."
        )

    db.commit()


def rollback_emails(dry_run: bool = DRY_RUN) -> int:
    db: Session = SessionLocal()
    processed = 0
    restored = 0
    failed = 0

    try:
        _ensure_rollback_schema(db)

        _log(db, action="email_encryption_rollback_batch", status="started")
        db.commit()

        last_id = 0
        while True:
            batch = (
                db.query(User)
                .filter(User.email.is_(None), User.email_encrypted.isnot(None), User.id > last_id)
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
                        encrypted_email = cast(str | None, user.email_encrypted)
                        if not encrypted_email:
                            raise ValueError("Encrypted email missing")

                        restored_email = decrypt_email(encrypted_email)
                        if not restored_email:
                            raise ValueError("Decrypted email is empty")

                        if not dry_run:
                            setattr(user, "email", restored_email)
                            setattr(user, "email_encrypted", None)
                            setattr(user, "email_hmac", None)

                        _log(
                            db,
                            action="email_encryption_rollback",
                            status="success",
                            user_id=user_id,
                        )
                    restored += 1
                except (ValueError, TypeError, OSError, RuntimeError, SQLAlchemyError) as exc:
                    failed += 1
                    _log(
                        db,
                        action="email_encryption_rollback",
                        status="error",
                        user_id=user_id,
                        error_message=safe_error_message(exc),
                    )

            db.commit()
            last_id = batch[-1].id
            if len(batch) < BATCH_SIZE:
                break

        summary = f"processed={processed},restored={restored},failed={failed},dry_run={int(dry_run)}"
        _log(db, action="email_encryption_rollback_batch", status="completed", error_message=summary)
        db.commit()
        return 0 if failed == 0 else 2
    except (ValueError, TypeError, OSError, RuntimeError, SQLAlchemyError) as exc:
        db.rollback()
        _log(
            db,
            action="email_encryption_rollback_batch",
            status="failed",
            error_message=safe_error_message(exc),
        )
        db.commit()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    code = rollback_emails()
    print("Rollback complete." if code == 0 else "Rollback finished with errors.")
    sys.exit(code)
