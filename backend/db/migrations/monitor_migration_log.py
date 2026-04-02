"""Monitoring utility for migration_log table with alert-style exit codes."""

from datetime import datetime, timezone
import os
import sys

from db.database import SessionLocal
from db.models import MigrationLog


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_monitoring() -> int:
    db = SessionLocal()
    try:
        threshold = int(os.getenv("MIGRATION_ERROR_THRESHOLD", "1"))

        error_count = (
            db.query(MigrationLog)
            .filter(MigrationLog.status.in_(["error", "failed"]))
            .count()
        )
        recent_errors = (
            db.query(MigrationLog)
            .filter(MigrationLog.status.in_(["error", "failed"]))
            .order_by(MigrationLog.timestamp.desc())
            .limit(10)
            .all()
        )

        print(f"[{_now_utc().isoformat()}] Migration monitor report")
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
