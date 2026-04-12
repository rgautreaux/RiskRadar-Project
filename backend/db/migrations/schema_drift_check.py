"""Schema drift checker for model metadata vs live database schema."""

from dataclasses import dataclass
from datetime import datetime, timezone
import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

database_module = import_module("db.database")
models_module = import_module("db.models")

SessionLocal = database_module.SessionLocal
Base = database_module.Base


@dataclass(frozen=True)
class DriftIssue:
    severity: str
    message: str


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _model_table_names() -> set[str]:
    return set(Base.metadata.tables.keys())


def _check_missing_tables(inspector: Inspector) -> list[DriftIssue]:
    model_tables = _model_table_names()
    db_tables = set(inspector.get_table_names())
    missing = sorted(model_tables - db_tables)
    if not missing:
        return []
    return [
        DriftIssue(
            severity="blocking",
            message=f"missing tables in database: {', '.join(missing)}",
        )
    ]


def _check_missing_columns(inspector: Inspector) -> list[DriftIssue]:
    issues: list[DriftIssue] = []
    for table_name, table in Base.metadata.tables.items():
        db_tables = set(inspector.get_table_names())
        if table_name not in db_tables:
            continue

        model_columns = {column.name for column in table.columns}
        db_columns = {column["name"] for column in inspector.get_columns(table_name)}
        missing_columns = sorted(model_columns - db_columns)
        if missing_columns:
            issues.append(
                DriftIssue(
                    severity="blocking",
                    message=f"{table_name} is missing columns: {', '.join(missing_columns)}",
                )
            )
    return issues


def _check_missing_indexes(inspector: Inspector) -> list[DriftIssue]:
    issues: list[DriftIssue] = []
    db_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in db_tables:
            continue

        required_index_names = {index.name for index in table.indexes if index.name}
        if not required_index_names:
            continue

        db_index_names = {index["name"] for index in inspector.get_indexes(table_name)}
        missing_indexes = sorted(required_index_names - db_index_names)
        if missing_indexes:
            issues.append(
                DriftIssue(
                    severity="blocking",
                    message=f"{table_name} is missing indexes: {', '.join(missing_indexes)}",
                )
            )
    return issues


def _check_missing_foreign_keys(inspector: Inspector) -> list[DriftIssue]:
    issues: list[DriftIssue] = []
    db_tables = set(inspector.get_table_names())

    for table_name, table in Base.metadata.tables.items():
        if table_name not in db_tables:
            continue

        model_fks: set[tuple[str, str, str]] = set()
        for fk in table.foreign_key_constraints:
            if len(fk.columns) != 1 or len(fk.elements) != 1:
                continue
            constrained = next(iter(fk.columns)).name
            element = fk.elements[0]
            referred_table = element.column.table.name
            referred_column = element.column.name
            model_fks.add((constrained, referred_table, referred_column))

        if not model_fks:
            continue

        db_fks: set[tuple[str, str, str]] = set()
        for fk in inspector.get_foreign_keys(table_name):
            constrained_columns = fk.get("constrained_columns") or []
            referred_columns = fk.get("referred_columns") or []
            referred_table = fk.get("referred_table")
            if len(constrained_columns) != 1 or len(referred_columns) != 1 or referred_table is None:
                continue
            db_fks.add((constrained_columns[0], referred_table, referred_columns[0]))

        missing_fks = sorted(model_fks - db_fks)
        if missing_fks:
            formatted = [f"{col}->{ref_table}.{ref_col}" for col, ref_table, ref_col in missing_fks]
            issues.append(
                DriftIssue(
                    severity="blocking",
                    message=f"{table_name} is missing foreign keys: {', '.join(formatted)}",
                )
            )

    return issues


def run_schema_drift_check() -> int:
    """Return 0 when schema matches model metadata; 2 for blocking drift."""
    db = SessionLocal()
    try:
        inspector = inspect(db.get_bind())

        issues: list[DriftIssue] = []
        issues.extend(_check_missing_tables(inspector))
        issues.extend(_check_missing_columns(inspector))
        issues.extend(_check_missing_indexes(inspector))
        issues.extend(_check_missing_foreign_keys(inspector))

        print(f"[{_now_utc().isoformat()}] Schema drift report")
        if not issues:
            print("status=ok")
            return 0

        for issue in issues:
            print(f"severity={issue.severity} message={issue.message}")
        print(f"blocking_issue_count={len(issues)}")
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(run_schema_drift_check())
