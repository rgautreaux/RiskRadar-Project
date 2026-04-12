"""Backfill users.alert_types JSON into user_alert_type_preferences rows."""

import json
from datetime import datetime, timezone
from importlib import import_module
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

models_module = import_module("db.models")
database_module = import_module("db.database")
normalization_module = import_module("db.normalization")

SessionLocal = database_module.SessionLocal
User = models_module.User
MigrationLog = models_module.MigrationLog
set_user_alert_types = normalization_module.set_user_alert_types


def _now() -> datetime:
    return datetime.now(timezone.utc)


def run_backfill(batch_size: int = 200) -> int:
    db = SessionLocal()
    processed = 0
    try:
        offset = 0
        db.add(MigrationLog(action="user_alert_type_backfill_batch", status="started", timestamp=_now()))
        db.commit()

        while True:
            rows = (
                db.query(User)
                .order_by(User.id.asc())
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            for user in rows:
                raw = user.alert_types or '["all"]'
                try:
                    decoded = json.loads(raw)
                    if not isinstance(decoded, list):
                        decoded = ["all"]
                    set_user_alert_types(db, user, decoded, dual_write_legacy=True)
                    processed += 1
                except Exception as exc:
                    db.add(
                        MigrationLog(
                            action="user_alert_type_backfill",
                            status="error",
                            timestamp=_now(),
                            user_id=user.id,
                            error_message=str(exc)[:500],
                        )
                    )
            db.commit()
            offset += batch_size

        db.add(
            MigrationLog(
                action="user_alert_type_backfill_batch",
                status="completed",
                timestamp=_now(),
                error_message=f"processed={processed}",
            )
        )
        db.commit()
        print(f"processed={processed}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(run_backfill())
