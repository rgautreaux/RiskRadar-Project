import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.db.database import SessionLocal
from backend.db.models import (
    Alert,
    AlertArchive,
    CleanupRun,
    ScrapeLog,
    ScrapeLogArchive,
    Summary,
    SummaryArchive,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetentionSpec:
    table_name: str
    model: Any
    archive_model: Any
    time_field: str
    retention_days: int


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _cutoff_utc(retention_days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=retention_days)


def _estimate_row_bytes(rows: list[Any]) -> int:
    if not rows:
        return 0
    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append({column.name: getattr(row, column.name) for column in row.__table__.columns})
    return len(json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"))


def _build_archive_row(row: Any, archive_model: Any, cleanup_run_id: int) -> Any:
    payload = {
        column.name: getattr(row, column.name)
        for column in row.__table__.columns
        if column.name != "id"
    }
    payload["original_id"] = row.id
    payload["cleanup_run_id"] = cleanup_run_id
    payload["archived_at"] = _now_utc()
    return archive_model(**payload)


def _table_specs_for_schedule(schedule_kind: str) -> list[RetentionSpec]:
    if schedule_kind == "nightly":
        return [
            RetentionSpec(
                table_name="scrape_log",
                model=ScrapeLog,
                archive_model=ScrapeLogArchive,
                time_field="completed_at",
                retention_days=settings.RETENTION_SCRAPE_LOG_DAYS,
            )
        ]

    return [
        RetentionSpec(
            table_name="alerts",
            model=Alert,
            archive_model=AlertArchive,
            time_field="created_at",
            retention_days=settings.RETENTION_ALERTS_DAYS,
        ),
        RetentionSpec(
            table_name="summaries",
            model=Summary,
            archive_model=SummaryArchive,
            time_field="created_at",
            retention_days=settings.RETENTION_SUMMARIES_DAYS,
        ),
        RetentionSpec(
            table_name="scrape_log",
            model=ScrapeLog,
            archive_model=ScrapeLogArchive,
            time_field="completed_at",
            retention_days=settings.RETENTION_SCRAPE_LOG_DAYS,
        ),
    ]


def _run_table_cleanup(db: Session, spec: RetentionSpec, schedule_kind: str) -> CleanupRun:
    started_at = _now_utc()
    start_time = datetime.now(timezone.utc)
    cutoff_at = _cutoff_utc(spec.retention_days)
    batch_size = max(1, settings.RETENTION_BATCH_SIZE)
    max_rows = max(batch_size, settings.RETENTION_MAX_ROWS_PER_RUN)

    base_query = db.query(spec.model).filter(getattr(spec.model, spec.time_field) < cutoff_at)
    eligible_rows = int(base_query.count() or 0)

    run_record = CleanupRun(
        table_name=spec.table_name,
        schedule_kind=schedule_kind,
        cutoff_at=cutoff_at,
        rows_eligible=min(eligible_rows, max_rows),
        dry_run=1 if settings.RETENTION_DRY_RUN else 0,
        started_at=started_at,
        completed_at=started_at,
    )
    db.add(run_record)
    db.flush()

    if settings.RETENTION_DRY_RUN:
        probe_rows = (
            base_query
            .order_by(spec.model.id.asc())
            .limit(min(batch_size, max_rows))
            .all()
        )
        run_record.storage_bytes_estimated = _estimate_row_bytes(probe_rows)
    else:
        rows_deleted = 0
        rows_archived = 0
        bytes_estimated = 0

        while rows_deleted < max_rows:
            limit_size = min(batch_size, max_rows - rows_deleted)
            rows = (
                base_query
                .order_by(spec.model.id.asc())
                .limit(limit_size)
                .all()
            )
            if not rows:
                break

            bytes_estimated += _estimate_row_bytes(rows)
            cleanup_run_id = cast(int, run_record.id)
            archive_rows = [_build_archive_row(row, spec.archive_model, cleanup_run_id) for row in rows]
            db.add_all(archive_rows)

            row_ids = [row.id for row in rows]
            db.query(spec.model).filter(spec.model.id.in_(row_ids)).delete(synchronize_session=False)

            rows_archived += len(rows)
            rows_deleted += len(rows)
            db.flush()

        run_record.rows_archived = rows_archived
        run_record.rows_deleted = rows_deleted
        run_record.storage_bytes_estimated = bytes_estimated

    run_record.completed_at = _now_utc()
    run_record.duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
    return run_record


def run_retention_cleanup(schedule_kind: str = "weekly") -> list[CleanupRun]:
    if not settings.RETENTION_ENABLED:
        logger.info("Retention cleanup skipped: RETENTION_ENABLED is false")
        return []

    records: list[CleanupRun] = []
    db = SessionLocal()
    try:
        specs = _table_specs_for_schedule(schedule_kind)
        for spec in specs:
            try:
                run_record = _run_table_cleanup(db, spec, schedule_kind)
                db.commit()
                db.refresh(run_record)
                records.append(run_record)
                logger.info(
                    "Retention cleanup finished table=%s schedule=%s dry_run=%s eligible=%s archived=%s deleted=%s bytes_est=%s duration_ms=%s",
                    run_record.table_name,
                    run_record.schedule_kind,
                    bool(run_record.dry_run),
                    run_record.rows_eligible,
                    run_record.rows_archived,
                    run_record.rows_deleted,
                    run_record.storage_bytes_estimated,
                    run_record.duration_ms,
                )
            except (SQLAlchemyError, ValueError, RuntimeError) as exc:
                db.rollback()
                error_record = CleanupRun(
                    table_name=spec.table_name,
                    schedule_kind=schedule_kind,
                    cutoff_at=_cutoff_utc(spec.retention_days),
                    dry_run=1 if settings.RETENTION_DRY_RUN else 0,
                    status="failed",
                    error_message=str(exc),
                    started_at=_now_utc(),
                    completed_at=_now_utc(),
                )
                db.add(error_record)
                db.commit()
                records.append(error_record)
                logger.exception("Retention cleanup failed for table=%s", spec.table_name)
        return records
    finally:
        db.close()
