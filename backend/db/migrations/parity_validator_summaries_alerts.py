"""Validate parity between summaries.alert_ids and summary_alerts rows."""

import json
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
Summary = models_module.Summary
get_summary_alert_ids = normalization_module.get_summary_alert_ids


def run_validator() -> int:
    db = SessionLocal()
    mismatches = 0
    try:
        rows = db.query(Summary).all()
        for summary in rows:
            legacy_raw = summary.alert_ids or "[]"
            try:
                legacy = sorted(int(item) for item in json.loads(legacy_raw))
            except Exception:
                legacy = []
            relational = sorted(get_summary_alert_ids(db, summary))
            if legacy != relational:
                mismatches += 1

        print(f"mismatches={mismatches}")
        return 0 if mismatches == 0 else 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(run_validator())
