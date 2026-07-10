"""Scheduler — runs each scraper on a timed interval."""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from config.settings import settings
from db.retention import run_retention_cleanup
from scrapers.registry import load_all_scrapers

logger = logging.getLogger(__name__)


def start_scheduler() -> BackgroundScheduler:
    # Allow tests to monkeypatch the top-level `scrapers.scheduler` shim's
    # BackgroundScheduler class. If present, prefer that so tests can inject
    # a FakeScheduler implementation.
    try:
        import scrapers.scheduler as _top_scheduler
        if hasattr(_top_scheduler, "BackgroundScheduler"):
            SchedulerCls = getattr(_top_scheduler, "BackgroundScheduler")
        else:
            SchedulerCls = BackgroundScheduler
    except Exception:
        SchedulerCls = BackgroundScheduler

    scheduler = SchedulerCls()
    default_interval = settings.SCRAPE_INTERVAL_MINUTES
    now = datetime.now(timezone.utc)

    scrapers = load_all_scrapers()

    for entry in scrapers:
        interval = entry["interval_minutes"] or default_interval
        offset = entry["stagger_offset_minutes"]

        scheduler.add_job(
            entry["scraper"].run,
            "interval",
            minutes=interval,
            next_run_time=now + timedelta(minutes=offset),
            id=entry["id"],
        )
        logger.info(
            f"Registered scraper '{entry['id']}': "
            f"interval={interval}m, first_run=+{offset}m"
        )

    if settings.RETENTION_ENABLED:
        scheduler.add_job(
            run_retention_cleanup,
            "cron",
            hour=settings.RETENTION_NIGHTLY_HOUR_UTC,
            minute=0,
            kwargs={"schedule_kind": "nightly"},
            id="retention_nightly",
            replace_existing=True,
        )
        logger.info(
            "Registered retention job 'retention_nightly': day=*, hour=%s, minute=0 UTC",
            settings.RETENTION_NIGHTLY_HOUR_UTC,
        )

        scheduler.add_job(
            run_retention_cleanup,
            "cron",
            day_of_week=settings.RETENTION_WEEKLY_DAY_UTC,
            hour=settings.RETENTION_WEEKLY_HOUR_UTC,
            minute=0,
            kwargs={"schedule_kind": "weekly"},
            id="retention_weekly",
            replace_existing=True,
        )
        logger.info(
            "Registered retention job 'retention_weekly': day=%s, hour=%s, minute=0 UTC",
            settings.RETENTION_WEEKLY_DAY_UTC,
            settings.RETENTION_WEEKLY_HOUR_UTC,
        )

    scheduler.start()
    logger.info(f"Scheduler started — {len(scrapers)} scrapers registered")
    # Provide a compatibility alias `jobs` for tests which inspect scheduled
    # jobs as a simple list. APScheduler exposes `get_jobs()`; expose it as
    # `jobs` when available so tests (and older code) can read `scheduler.jobs`.
    try:
        if hasattr(scheduler, "get_jobs") and not hasattr(scheduler, "jobs"):
            jobs_list = []
            for job in scheduler.get_jobs():
                # Convert APScheduler Job -> lightweight dict similar to the
                # FakeScheduler used in tests so callers can inspect `job["kwargs"]["id"]`.
                try:
                    kwargs = dict(job.kwargs or {})
                except Exception:
                    kwargs = {}
                if "id" not in kwargs:
                    try:
                        kwargs["id"] = job.id
                    except Exception:
                        pass
                jobs_list.append({"args": getattr(job, "args", None), "kwargs": kwargs})
            scheduler.jobs = jobs_list
    except Exception:
        # Best-effort only; don't crash startup for instrumentation purposes.
        pass
    return scheduler
