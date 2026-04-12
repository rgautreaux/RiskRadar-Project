"""Validate parity between users.alert_types and user_alert_type_preferences rows."""

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
User = models_module.User
get_user_alert_types = normalization_module.get_user_alert_types


def run_validator() -> int:
    db = SessionLocal()
    mismatches = 0
    try:
        rows = db.query(User).all()
        for user in rows:
            legacy_raw = user.alert_types or '["all"]'
            try:
                legacy = sorted(str(item) for item in json.loads(legacy_raw))
            except Exception:
                legacy = ["all"]
            relational = sorted(get_user_alert_types(db, user))
            if legacy != relational:
                mismatches += 1

        print(f"mismatches={mismatches}")
        return 0 if mismatches == 0 else 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(run_validator())
