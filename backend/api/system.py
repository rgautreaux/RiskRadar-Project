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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models import Alert, ScrapeLog, User
from auth.security import get_current_user

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Returns API status and basic database stats so you can verify
    the backend is running and connected to the database.
    """
    try:
        alert_count = db.query(func.count(Alert.id)).scalar() or 0
        last_scrape = (
            db.query(ScrapeLog)
            .order_by(ScrapeLog.completed_at.desc())
            .first()
        )
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "alert_count": alert_count,
            "last_scrape": {
                "source": last_scrape.source,
                "status": last_scrape.status,
                "completed_at": last_scrape.completed_at,
            } if last_scrape else None,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "error",
            "error": str(e),
        }


@router.post("/scrape/trigger")
def trigger_scrape(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger all scrapers to run immediately.

    This is the same pipeline that APScheduler executes on the
    30-minute interval. Requires authentication.

    Returns a summary of what each scraper fetched.
    """
    from scrapers.registry import load_all_scrapers

    scrapers = load_all_scrapers()
    results = []

    for scraper_info in scrapers:
        scraper = scraper_info["scraper"]
        try:
            count = scraper.run()
            results.append({
                "source": scraper_info["id"],
                "status": "success",
                "alerts_stored": count,
            })
        except Exception as e:
            results.append({
                "source": scraper_info["id"],
                "status": "error",
                "error": str(e),
            })

    return {"triggered_at": datetime.now(timezone.utc).isoformat(), "results": results}
