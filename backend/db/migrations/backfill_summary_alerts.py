"""Backfill summaries.alert_ids JSON into summary_alerts rows."""

import json
from datetime import datetime, timezone
from importlib import import_module
import sys
from pathlib import Path

from sqlalchemy import text

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

models_module = import_module("db.models")
database_module = import_module("db.database")
normalization_module = import_module("db.normalization")

SessionLocal = database_module.SessionLocal
Summary = models_module.Summary
MigrationLog = models_module.MigrationLog
set_summary_alert_ids = normalization_module.set_summary_alert_ids


def _now() -> datetime:
    return datetime.now(timezone.utc)


def run_backfill(batch_size: int = 200) -> int:
    db = SessionLocal()
    processed = 0
    try:
        offset = 0
        db.add(MigrationLog(action="summary_alerts_backfill_batch", status="started", timestamp=_now()))
        db.commit()

        while True:
            rows = (
                db.query(Summary)
                .order_by(Summary.id.asc())
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            for summary in rows:
                if not summary.alert_ids:
                    continue
                try:
                    raw = json.loads(summary.alert_ids)
                    if not isinstance(raw, list):
                        continue
                    ids = [int(item) for item in raw]
                    set_summary_alert_ids(db, summary, ids, dual_write_legacy=True)
                    processed += 1
                except Exception as exc:
                    db.add(
                        MigrationLog(
                            action="summary_alerts_backfill",
                            status="error",
                            timestamp=_now(),
                            user_id=summary.id,
                            error_message=str(exc)[:500],
                        )
                    )
            db.commit()
            offset += batch_size

        db.add(
            MigrationLog(
                action="summary_alerts_backfill_batch",
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
