"""Scheduler — runs each scraper on a timed interval."""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from config.settings import settings
from scrapers.nws_scraper import NWSScraper
from scrapers.airnow_scraper import AirNowScraper
from scrapers.epa_scraper import EPAScraper
from scrapers.firms_scraper import FIRMSScraper

logger = logging.getLogger(__name__)


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    interval = settings.SCRAPE_INTERVAL_MINUTES
    now = datetime.now(timezone.utc)

    # NWS — no key needed, run immediately
    scheduler.add_job(
        NWSScraper().run,
        "interval",
        minutes=interval,
        next_run_time=now,
        id="nws",
    )

    # AirNow — needs API key
    if settings.AIRNOW_API_KEY:
        scheduler.add_job(
            AirNowScraper().run,
            "interval",
            minutes=interval,
            next_run_time=now + timedelta(minutes=1),
            id="airnow",
        )

    # EPA — no key needed, less frequent
    scheduler.add_job(
        EPAScraper().run,
        "interval",
        minutes=60,
        next_run_time=now + timedelta(minutes=3),
        id="epa",
    )

    # NASA FIRMS — needs API key
    if settings.NASA_FIRMS_MAP_KEY:
        scheduler.add_job(
            FIRMSScraper().run,
            "interval",
            minutes=interval,
            next_run_time=now + timedelta(minutes=5),
            id="firms",
        )

    scheduler.start()
    logger.info("Scheduler started — scrapers registered")
    return scheduler
