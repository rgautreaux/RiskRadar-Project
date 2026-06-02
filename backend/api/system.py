"""
RiskRadar - System & admin API endpoints.

Endpoints:
  GET  /health          — Health check (public)
  POST /scrape/trigger  — Manually trigger a scrape run (protected)

HOW IT CONNECTS:
  - /health queries the database to verify connectivity.
  - /scrape/trigger runs all registered scrapers immediately
    (same ones that APScheduler runs on the 30-min interval).
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Alert, ScrapeLog, User
from auth.security import get_current_user

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check(_db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Health check endpoint.

    Returns API status and basic database stats so you can verify
    the backend is running and connected to the database.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        alert_count = _db.query(Alert.id).count() or 0
        last_scrape = (
            _db.query(ScrapeLog)
            .order_by(ScrapeLog.completed_at.desc())
            .first()
        )
        return {
            "status": "healthy",
            "timestamp": timestamp,
            "database": "connected",
            "alert_count": alert_count,
            "last_scrape": {
                "source": last_scrape.source,
                "status": last_scrape.status,
                "completed_at": last_scrape.completed_at,
            } if last_scrape else None,
        }
    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "timestamp": timestamp,
            "database": "disconnected",
            "alert_count": 0,
            "last_scrape": None,
        }


@router.post("/scrape/trigger")
def trigger_scrape(
    _db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Manually trigger all scrapers to run immediately.

    This is the same pipeline that APScheduler executes on the
    30-minute interval. Requires authentication.

    Returns a summary of what each scraper fetched.
    """
    # Import the top-level shim so tests can monkeypatch `scrapers.registry`.
    from scrapers.registry import load_all_scrapers

    _ = (_db, _current_user)
    scrapers = load_all_scrapers()
    results: list[dict[str, Any]] = []

    for scraper_info in scrapers:
        scraper = scraper_info["scraper"]
        try:
            count = scraper.run()
            results.append({
                "source": scraper_info["id"],
                "status": "success",
                "alerts_stored": count,
            })
        except Exception as exc:
            # Don't let one failing scraper crash the entire trigger endpoint;
            # surface the failure per-scraper so callers can observe partial
            # failures (tests expect this behavior).
            results.append({
                "source": scraper_info["id"],
                "status": "error",
                "alerts_stored": 0,
                "error": str(exc),
            })

    return {"triggered_at": datetime.now(timezone.utc).isoformat(), "results": results}
