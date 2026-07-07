from datetime import datetime, timedelta, timezone

from db.models import Alert, AlertArchive, CleanupRun, ScrapeLog, ScrapeLogArchive
from db.retention import run_retention_cleanup


def _days_ago(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_retention_dry_run_logs_without_deleting(db_session, monkeypatch):
    old_alert = Alert(
        source="nws",
        source_id="old_alert",
        alert_type="weather",
        severity="high",
        title="Old Alert",
        created_at=_days_ago(500),
        fetched_at=_days_ago(500),
        updated_at=_days_ago(500),
    )
    db_session.add(old_alert)
    db_session.commit()

    monkeypatch.setattr("db.retention.SessionLocal", lambda: db_session)
    monkeypatch.setattr("db.retention.settings.RETENTION_ENABLED", True)
    monkeypatch.setattr("db.retention.settings.RETENTION_DRY_RUN", True)
    monkeypatch.setattr("db.retention.settings.RETENTION_BATCH_SIZE", 50)
    monkeypatch.setattr("db.retention.settings.RETENTION_MAX_ROWS_PER_RUN", 500)
    monkeypatch.setattr("db.retention.settings.RETENTION_ALERTS_DAYS", 365)

    records = run_retention_cleanup(schedule_kind="weekly")

    assert records
    assert db_session.query(Alert).count() == 1
    assert db_session.query(AlertArchive).count() == 0

    alert_run = (
        db_session.query(CleanupRun)
        .filter(CleanupRun.table_name == "alerts")
        .order_by(CleanupRun.id.desc())
        .first()
    )
    assert alert_run is not None
    assert alert_run.rows_eligible >= 1
    assert alert_run.rows_deleted == 0
    assert alert_run.rows_archived == 0
    assert alert_run.dry_run == 1


def test_retention_archives_and_deletes_in_batches(db_session, monkeypatch):
    old_logs = [
        ScrapeLog(
            source="nws",
            status="success",
            alerts_fetched=3,
            alerts_new=2,
            started_at=_days_ago(130),
            completed_at=_days_ago(130),
        ),
        ScrapeLog(
            source="epa",
            status="success",
            alerts_fetched=2,
            alerts_new=1,
            started_at=_days_ago(131),
            completed_at=_days_ago(131),
        ),
        ScrapeLog(
            source="usgs_earthquakes",
            status="success",
            alerts_fetched=1,
            alerts_new=1,
            started_at=_days_ago(132),
            completed_at=_days_ago(132),
        ),
    ]
    db_session.add_all(old_logs)
    db_session.commit()

    monkeypatch.setattr("db.retention.SessionLocal", lambda: db_session)
    monkeypatch.setattr("db.retention.settings.RETENTION_ENABLED", True)
    monkeypatch.setattr("db.retention.settings.RETENTION_DRY_RUN", False)
    monkeypatch.setattr("db.retention.settings.RETENTION_BATCH_SIZE", 2)
    monkeypatch.setattr("db.retention.settings.RETENTION_MAX_ROWS_PER_RUN", 10)
    monkeypatch.setattr("db.retention.settings.RETENTION_SCRAPE_LOG_DAYS", 90)

    run_retention_cleanup(schedule_kind="nightly")

    assert db_session.query(ScrapeLog).count() == 0
    assert db_session.query(ScrapeLogArchive).count() == 3

    log_run = (
        db_session.query(CleanupRun)
        .filter(CleanupRun.table_name == "scrape_log")
        .order_by(CleanupRun.id.desc())
        .first()
    )
    assert log_run is not None
    assert log_run.rows_archived == 3
    assert log_run.rows_deleted == 3
    assert log_run.dry_run == 0


def test_scheduler_registers_retention_jobs_when_enabled(monkeypatch):
    from scrapers import scheduler as scheduler_module

    class FakeScheduler:
        def __init__(self):
            self.jobs = []
            self.started = False

        def add_job(self, *args, **kwargs):
            self.jobs.append({"args": args, "kwargs": kwargs})

        def start(self):
            self.started = True

    monkeypatch.setattr(scheduler_module, "BackgroundScheduler", FakeScheduler)
    monkeypatch.setattr(scheduler_module, "load_all_scrapers", lambda: [])
    monkeypatch.setattr("scrapers.scheduler.settings.RETENTION_ENABLED", True)
    monkeypatch.setattr("scrapers.scheduler.settings.RETENTION_NIGHTLY_HOUR_UTC", 2)
    monkeypatch.setattr("scrapers.scheduler.settings.RETENTION_WEEKLY_DAY_UTC", "sun")
    monkeypatch.setattr("scrapers.scheduler.settings.RETENTION_WEEKLY_HOUR_UTC", 4)

    scheduler = scheduler_module.start_scheduler()

    job_ids = [job["kwargs"]["id"] for job in scheduler.jobs]
    assert "retention_nightly" in job_ids
    assert "retention_weekly" in job_ids
    assert scheduler.started is True
