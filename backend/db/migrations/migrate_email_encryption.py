"""
Migration Script: Encrypt and HMAC Existing User Emails

This script migrates all users in the database:
- Encrypts the plaintext email into email_encrypted
- Computes HMAC for email_hmac
- Sets legacy email field to None (for privacy)
- Logs batch start/end and per-user actions to MigrationLog

Run this script in a safe environment after backing up the database.
"""

from datetime import datetime, timezone
import re
import sys

from sqlalchemy.orm import Session

from auth.security import encrypt_email, email_hmac
from db.database import SessionLocal
from db.models import MigrationLog, User


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_ERROR_LENGTH = 500


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


def migrate_emails() -> int:
    db: Session = SessionLocal()
    processed = 0
    succeeded = 0
    failed = 0

    try:
        _log(db, action="email_encryption_batch", status="started")
        db.commit()

        users = (
            db.query(User)
            .filter(User.email.isnot(None))
            .order_by(User.id.asc())
            .all()
        )

        for user in users:
            processed += 1
            try:
                original_email = user.email
                if not original_email:
                    raise ValueError("User email is empty")

                user.email_encrypted = encrypt_email(original_email)
                user.email_hmac = email_hmac(original_email)
                user.email = None

                _log(db, action="email_encryption", status="success", user_id=user.id)
                db.commit()
                succeeded += 1
            except Exception as exc:  # noqa: BLE001 - capture migration/user-level failures safely
                db.rollback()
                failed += 1
                _log(
                    db,
                    action="email_encryption",
                    status="error",
                    user_id=user.id,
                    error_message=safe_error_message(exc),
                )
                db.commit()

        summary = f"processed={processed},succeeded={succeeded},failed={failed}"
        _log(db, action="email_encryption_batch", status="completed", error_message=summary)
        db.commit()
        return 0 if failed == 0 else 2
    except Exception as exc:  # noqa: BLE001 - capture batch-level failure and persist audit record
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
