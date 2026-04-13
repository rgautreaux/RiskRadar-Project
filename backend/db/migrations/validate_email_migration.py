"""Validation utility for email encryption migration in staging/local environments."""

from datetime import datetime, timezone
import sys
from importlib import import_module
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

database_module = import_module("db.database")
models_module = import_module("db.models")

SessionLocal = database_module.SessionLocal
MigrationLog = models_module.MigrationLog
User = models_module.User


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_validation() -> int:
    db = SessionLocal()
    try:
        users_total = db.query(User).count()
        users_plaintext_remaining = db.query(User).filter(User.email.isnot(None)).count()
        users_missing_encrypted = db.query(User).filter(User.email.is_(None), User.email_encrypted.is_(None)).count()
        users_missing_hmac = db.query(User).filter(User.email.is_(None), User.email_hmac.is_(None)).count()

        last_batch_started = (
            db.query(MigrationLog)
            .filter(
                MigrationLog.action == "email_encryption_batch",
                MigrationLog.status == "started",
            )
            .order_by(MigrationLog.timestamp.desc())
            .first()
        )

        failed_logs_query = db.query(MigrationLog).filter(
            MigrationLog.action.in_(["email_encryption", "email_encryption_batch"]),
            MigrationLog.status.in_(["failed", "error"]),
        )
        batch_completed_query = db.query(MigrationLog).filter(
            MigrationLog.action == "email_encryption_batch",
            MigrationLog.status == "completed",
        )

        if last_batch_started is not None:
            failed_logs_query = failed_logs_query.filter(MigrationLog.timestamp >= last_batch_started.timestamp)
            batch_completed_query = batch_completed_query.filter(MigrationLog.timestamp >= last_batch_started.timestamp)

        failed_logs = failed_logs_query.count()
        batch_completed = batch_completed_query.count()
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
