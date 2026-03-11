"""Scheduler — runs each scraper on a timed interval."""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from config.settings import settings
from db.retention import run_retention_cleanup
from scrapers.registry import load_all_scrapers

logger = logging.getLogger(__name__)


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
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
    return scheduler
