"""Validation utility for email encryption migration in staging/local environments."""

from datetime import datetime, timezone
import sys

from db.database import SessionLocal
from db.models import MigrationLog, User


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_validation() -> int:
    db = SessionLocal()
    try:
        users_total = db.query(User).count()
        users_plaintext_remaining = db.query(User).filter(User.email.isnot(None)).count()
        users_missing_encrypted = db.query(User).filter(User.email.is_(None), User.email_encrypted.is_(None)).count()
        users_missing_hmac = db.query(User).filter(User.email.is_(None), User.email_hmac.is_(None)).count()

        failed_logs = db.query(MigrationLog).filter(MigrationLog.status.in_(["failed", "error"])) .count()
        batch_completed = (
            db.query(MigrationLog)
            .filter(
                MigrationLog.action == "email_encryption_batch",
                MigrationLog.status == "completed",
            )
            .count()
        )

        print(f"[{_now_utc().isoformat()}] Email migration validation report")
        print(f"users_total={users_total}")
        print(f"users_plaintext_remaining={users_plaintext_remaining}")
        print(f"users_missing_encrypted={users_missing_encrypted}")
        print(f"users_missing_hmac={users_missing_hmac}")
        print(f"migration_failed_or_error_logs={failed_logs}")
        print(f"batch_completed_records={batch_completed}")

        checks_ok = (
            users_plaintext_remaining == 0
            and users_missing_encrypted == 0
            and users_missing_hmac == 0
            and failed_logs == 0
            and batch_completed >= 1
        )
        return 0 if checks_ok else 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(run_validation())
