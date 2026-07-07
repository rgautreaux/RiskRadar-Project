"""Monitoring utility for migration_log table with alert-style exit codes."""

from datetime import datetime, timezone
import os
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


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_monitoring() -> int:
    db = SessionLocal()
    try:
        raw_threshold = os.getenv("MIGRATION_ERROR_THRESHOLD", "1")
        try:
            threshold = int(raw_threshold)
        except ValueError:
            print(
                f"Invalid MIGRATION_ERROR_THRESHOLD value {raw_threshold!r}; "
                "defaulting to 1"
            )
            threshold = 1

        if threshold <= 0:
            print(
                f"Non-positive MIGRATION_ERROR_THRESHOLD value {threshold!r}; "
                "defaulting to 1"
            )
            threshold = 1

        latest_batch = (
            db.query(MigrationLog)
            .filter(
                MigrationLog.action == "email_encryption_batch",
                MigrationLog.status == "started",
            )
            .order_by(MigrationLog.timestamp.desc())
            .first()
        )

        if latest_batch is None:
            error_count = 0
            recent_errors: list[MigrationLog] = []
        else:
            batch_started_at = latest_batch.timestamp
            scoped_errors = (
                db.query(MigrationLog)
                .filter(
                    MigrationLog.action == "email_encryption",
                    MigrationLog.status.in_(["error", "failed"]),
                    MigrationLog.timestamp >= batch_started_at,
                )
            )
            error_count = scoped_errors.count()
            recent_errors = list(
                scoped_errors
                .order_by(MigrationLog.timestamp.desc())
                .limit(10)
                .all()
            )

        print(f"[{_now_utc().isoformat()}] Migration monitor report")
        if latest_batch is None:
            print("latest_batch_started_at=None")
            print("No email_encryption_batch start found; monitoring current batch only")
        else:
            print(f"latest_batch_started_at={latest_batch.timestamp}")
        print(f"error_count={error_count}")
        print(f"threshold={threshold}")

        for row in recent_errors:
            print(
                f"timestamp={row.timestamp} action={row.action} status={row.status} "
                f"user_id={row.user_id} error_message={row.error_message}"
            )

        if error_count >= threshold:
            print("ALERT: migration error threshold reached")
            return 2

        print("OK: migration error threshold not reached")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(run_monitoring())
