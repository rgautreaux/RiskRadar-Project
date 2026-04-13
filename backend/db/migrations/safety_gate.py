"""Unified migration safety gate for staging/production readiness checks."""

from datetime import datetime, timezone
import os
import sys
from importlib import import_module
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

preflight_module = import_module("db.migrations.preflight")
schema_drift_module = import_module("db.migrations.schema_drift_check")
validator_module = import_module("db.migrations.validate_email_migration")
monitor_module = import_module("db.migrations.monitor_migration_log")

run_preflight = preflight_module.run_preflight
run_schema_drift_check = schema_drift_module.run_schema_drift_check
run_validation = validator_module.run_validation
run_monitoring = monitor_module.run_monitoring


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_safety_gate() -> int:
    """Run migration safety checks in strict sequence.

    Returns 0 when all checks pass, otherwise 2.
    """
    preflight_strict = os.getenv("MIGRATION_PREFLIGHT_STRICT", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    normalization_contract_required = os.getenv(
        "MIGRATION_NORMALIZATION_CONTRACT_REQUIRED",
        "false",
    ).lower() in {"1", "true", "yes", "on"}

    print(f"[{_now_utc().isoformat()}] Migration safety gate")
    print(f"preflight_strict={preflight_strict}")
    print(f"normalization_contract_required={normalization_contract_required}")

    checks: list[tuple[str, int]] = [
        (
            "preflight",
            run_preflight(strict=preflight_strict, enforce_contract=normalization_contract_required),
        ),
        ("schema_drift", run_schema_drift_check()),
        ("validation", run_validation()),
        ("monitor", run_monitoring()),
    ]

    failed_checks = [name for name, code in checks if code != 0]
    for name, code in checks:
        print(f"check={name} code={code}")

    if failed_checks:
        print(f"status=failed failed_checks={','.join(failed_checks)}")
        return 2

    print("status=ok")
    return 0


if __name__ == "__main__":
    sys.exit(run_safety_gate())
