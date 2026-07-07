"""Preflight checks for schema and data integrity before database migrations."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy import inspect, select
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

database_module = import_module("db.database")
models_module = import_module("db.models")

SessionLocal = database_module.SessionLocal
Alert = models_module.Alert
AlertArchive = models_module.AlertArchive
CleanupRun = models_module.CleanupRun
NotificationDispatchLog = models_module.NotificationDispatchLog
ScrapeLog = models_module.ScrapeLog
ScrapeLogArchive = models_module.ScrapeLogArchive
Summary = models_module.Summary
SummaryAlert = models_module.SummaryAlert
SummaryArchive = models_module.SummaryArchive
User = models_module.User
UserAlertTypePreference = models_module.UserAlertTypePreference
AlertRawPayload = models_module.AlertRawPayload


@dataclass(frozen=True)
class PreflightIssue:
    severity: str
    message: str


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _missing_items(actual: Iterable[str], expected: Iterable[str]) -> list[str]:
    actual_set = set(actual)
    return [item for item in expected if item not in actual_set]


def _check_required_tables(inspector: Inspector) -> list[PreflightIssue]:
    required_tables = [
        "alerts",
        "summaries",
        "users",
        "scrape_log",
        "summary_alerts",
        "user_alert_type_preferences",
        "zip_geo",
        "locations",
        "alert_raw_payloads",
        "alerts_archive",
        "summaries_archive",
        "scrape_log_archive",
        "cleanup_runs",
        "migration_log",
        "notification_dispatch_log",
    ]
    missing_tables = _missing_items(inspector.get_table_names(), required_tables)
    if not missing_tables:
        return []
    return [
        PreflightIssue(
            severity="blocking",
            message=f"missing required tables: {', '.join(missing_tables)}",
        )
    ]


def _check_required_columns(inspector: Inspector, existing_tables: set[str]) -> list[PreflightIssue]:
    required_columns = {
        "users": ["email_encrypted", "email_hmac", "notify_push", "notify_email", "notify_sms"],
        "cleanup_runs": ["table_name", "schedule_kind", "cutoff_at", "started_at", "completed_at"],
        "notification_dispatch_log": [
            "alert_id",
            "initiated_by_user_id",
            "provider",
            "created_at",
        ],
        "alerts_archive": ["original_id", "cleanup_run_id", "archived_at"],
        "summaries_archive": ["original_id", "cleanup_run_id", "archived_at"],
        "scrape_log_archive": ["original_id", "cleanup_run_id", "archived_at"],
        "alerts": ["location_id"],
    }

    issues: list[PreflightIssue] = []
    for table_name, expected_columns in required_columns.items():
        if table_name not in existing_tables:
            continue
        actual_columns = [column["name"] for column in inspector.get_columns(table_name)]
        missing_columns = _missing_items(actual_columns, expected_columns)
        if missing_columns:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=f"{table_name} is missing columns: {', '.join(missing_columns)}",
                )
            )
    return issues


def _check_unique_email_hmac(db: Session) -> list[PreflightIssue]:
    email_hmac_values = list(
        db.execute(select(User.email_hmac).where(User.email_hmac.isnot(None))).scalars().all()
    )
    duplicate_rows = sum(1 for count in Counter(email_hmac_values).values() if count > 1)
    if duplicate_rows:
        return [
            PreflightIssue(
                severity="blocking",
                message=f"users.email_hmac has {duplicate_rows} duplicate value group(s)",
            )
        ]
    return []


def _check_plaintext_email_leftovers(db: Session) -> list[PreflightIssue]:
    plaintext_count = db.query(User).filter(User.email.isnot(None)).count()
    if plaintext_count:
        return [
            PreflightIssue(
                severity="blocking",
                message=f"users has {plaintext_count} plaintext email row(s) remaining",
            )
        ]
    return []


def _check_archive_lineage(db: Session) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []

    inspector = inspect(db.get_bind())
    if not inspector.has_table("cleanup_runs"):
        return issues
    if not inspector.has_table("alerts_archive") and not inspector.has_table("summaries_archive") and not inspector.has_table("scrape_log_archive"):
        return issues

    orphan_alert_archives = (
        db.query(AlertArchive)
        .filter(
            AlertArchive.cleanup_run_id.isnot(None),
            ~AlertArchive.cleanup_run_id.in_(db.query(CleanupRun.id)),
        )
        .count()
    )
    if orphan_alert_archives:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"alerts_archive has {orphan_alert_archives} orphaned cleanup_run_id value(s)",
            )
        )

    orphan_summary_archives = (
        db.query(SummaryArchive)
        .filter(
            SummaryArchive.cleanup_run_id.isnot(None),
            ~SummaryArchive.cleanup_run_id.in_(db.query(CleanupRun.id)),
        )
        .count()
    )
    if orphan_summary_archives:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"summaries_archive has {orphan_summary_archives} orphaned cleanup_run_id value(s)",
            )
        )

    orphan_scrape_log_archives = (
        db.query(ScrapeLogArchive)
        .filter(
            ScrapeLogArchive.cleanup_run_id.isnot(None),
            ~ScrapeLogArchive.cleanup_run_id.in_(db.query(CleanupRun.id)),
        )
        .count()
    )
    if orphan_scrape_log_archives:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"scrape_log_archive has {orphan_scrape_log_archives} orphaned cleanup_run_id value(s)",
            )
        )

    return issues


def _check_dispatch_references(db: Session) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []

    inspector = inspect(db.get_bind())
    if not inspector.has_table("alerts") or not inspector.has_table("users"):
        return issues
    if not inspector.has_table("notification_dispatch_log"):
        return issues

    orphan_alert_refs = (
        db.query(NotificationDispatchLog)
        .filter(~NotificationDispatchLog.alert_id.in_(db.query(Alert.id)))
        .count()
    )
    if orphan_alert_refs:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"notification_dispatch_log has {orphan_alert_refs} alert_id value(s) with no matching alerts row",
            )
        )

    orphan_user_refs = (
        db.query(NotificationDispatchLog)
        .filter(~NotificationDispatchLog.initiated_by_user_id.in_(db.query(User.id)))
        .count()
    )
    if orphan_user_refs:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"notification_dispatch_log has {orphan_user_refs} initiated_by_user_id value(s) with no matching users row",
            )
        )

    return issues


def _check_required_indexes(inspector: Inspector, existing_tables: set[str]) -> list[PreflightIssue]:
    required_indexes = {
        "alerts": ["idx_alerts_source_fetched_at", "idx_alerts_type_severity_fetched_at"],
        "summaries": ["idx_summaries_summary_type_generated_at"],
        "scrape_log": ["idx_scrape_log_source_started_at", "idx_scrape_log_status_completed_at"],
        "cleanup_runs": ["idx_cleanup_runs_status_started_at"],
        "notification_dispatch_log": [
            "idx_notification_dispatch_status_created_at",
            "idx_notification_dispatch_initiated_by_user_id",
        ],
    }

    issues: list[PreflightIssue] = []
    for table_name, expected_indexes in required_indexes.items():
        if table_name not in existing_tables:
            continue

        actual_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
        missing_indexes = [index_name for index_name in expected_indexes if index_name not in actual_indexes]
        if missing_indexes:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=f"{table_name} is missing indexes: {', '.join(missing_indexes)}",
                )
            )

    return issues


def _check_required_foreign_keys(inspector: Inspector, existing_tables: set[str]) -> list[PreflightIssue]:
    required_foreign_keys = {
        "alerts_archive": {("cleanup_run_id", "cleanup_runs", "id")},
        "summaries_archive": {("cleanup_run_id", "cleanup_runs", "id")},
        "scrape_log_archive": {("cleanup_run_id", "cleanup_runs", "id")},
        "notification_dispatch_log": {
            ("alert_id", "alerts", "id"),
            ("initiated_by_user_id", "users", "id"),
        },
    }

    issues: list[PreflightIssue] = []
    for table_name, expected_fks in required_foreign_keys.items():
        if table_name not in existing_tables:
            continue

        actual_fks: set[tuple[str, str, str]] = set()
        for fk in inspector.get_foreign_keys(table_name):
            constrained_columns = fk.get("constrained_columns") or []
            referred_columns = fk.get("referred_columns") or []
            referred_table = fk.get("referred_table")
            if len(constrained_columns) != 1 or len(referred_columns) != 1 or referred_table is None:
                continue
            actual_fks.add((constrained_columns[0], referred_table, referred_columns[0]))

        missing_fks = expected_fks - actual_fks
        if missing_fks:
            formatted = [f"{column}->{ref_table}.{ref_column}" for (column, ref_table, ref_column) in sorted(missing_fks)]
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=f"{table_name} is missing foreign keys: {', '.join(formatted)}",
                )
            )

    return issues


def _check_legacy_typo_schema(inspector: Inspector, existing_tables: set[str]) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []

    if "user_prefernces" in existing_tables:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message="legacy typo table detected: user_prefernces (expected user_preferences)",
            )
        )

    if "user_reads" in existing_tables:
        user_reads_columns = {column["name"] for column in inspector.get_columns("user_reads")}
        if "articlle_id" in user_reads_columns:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message="legacy typo column detected: user_reads.articlle_id (expected article_id)",
                )
            )

    return issues


def _check_normalization_contract_readiness(
    db: Session,
    inspector: Inspector,
    existing_tables: set[str],
) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []

    required_contract_tables = {
        "summary_alerts",
        "user_alert_type_preferences",
        "alert_raw_payloads",
    }
    missing = [name for name in sorted(required_contract_tables) if name not in existing_tables]
    if missing:
        issues.append(
            PreflightIssue(
                severity="blocking",
                message=f"normalization contract blocked: missing required table(s): {', '.join(missing)}",
            )
        )
        return issues

    summary_columns = {column["name"] for column in inspector.get_columns("summaries")}
    if "alert_ids" in summary_columns:
        legacy_summaries = db.query(Summary).filter(Summary.alert_ids.isnot(None)).count()
        relational_summaries = db.query(SummaryAlert.summary_id).distinct().count()
        if relational_summaries < legacy_summaries:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=(
                        "normalization contract blocked: summary_alerts parity incomplete "
                        f"(legacy_summaries={legacy_summaries}, relational_summaries={relational_summaries})"
                    ),
                )
            )

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "alert_types" in user_columns:
        legacy_users = db.query(User).filter(User.alert_types.isnot(None)).count()
        relational_users = db.query(UserAlertTypePreference.user_id).distinct().count()
        if relational_users < legacy_users:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=(
                        "normalization contract blocked: user_alert_type_preferences parity incomplete "
                        f"(legacy_users={legacy_users}, relational_users={relational_users})"
                    ),
                )
            )

    alert_columns = {column["name"] for column in inspector.get_columns("alerts")}
    if "raw_data" in alert_columns:
        legacy_alerts = db.query(Alert).filter(Alert.raw_data.isnot(None)).count()
        relational_alerts = db.query(AlertRawPayload.alert_id).count()
        if relational_alerts < legacy_alerts:
            issues.append(
                PreflightIssue(
                    severity="blocking",
                    message=(
                        "normalization contract blocked: alert_raw_payloads parity incomplete "
                        f"(legacy_alerts={legacy_alerts}, relational_alerts={relational_alerts})"
                    ),
                )
            )

    return issues


def run_preflight(strict: bool = False, enforce_contract: bool = False) -> int:
    """Run safety checks before applying a schema or data migration.

    Returns 0 when no blocking issues are found and 2 when at least one
    blocking issue is detected.
    """
    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())
        existing_tables = set(inspector.get_table_names())

        issues: list[PreflightIssue] = []
        issues.extend(_check_required_tables(inspector))
        issues.extend(_check_required_columns(inspector, existing_tables))
        issues.extend(_check_unique_email_hmac(db))
        if strict:
            issues.extend(_check_plaintext_email_leftovers(db))
        issues.extend(_check_required_indexes(inspector, existing_tables))
        issues.extend(_check_required_foreign_keys(inspector, existing_tables))
        issues.extend(_check_legacy_typo_schema(inspector, existing_tables))
        if enforce_contract:
            issues.extend(_check_normalization_contract_readiness(db, inspector, existing_tables))
        issues.extend(_check_archive_lineage(db))
        issues.extend(_check_dispatch_references(db))

        print(f"[{_now_utc().isoformat()}] Database preflight report")
        if strict:
            print("mode=strict")
        else:
            print("mode=standard")
        print(f"normalization_contract_enforced={enforce_contract}")

        if not issues:
            print("status=ok")
            return 0

        for issue in issues:
            print(f"severity={issue.severity} message={issue.message}")

        blocking_issues = [issue for issue in issues if issue.severity == "blocking"]
        print(f"blocking_issue_count={len(blocking_issues)}")
        return 2 if blocking_issues else 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(run_preflight())