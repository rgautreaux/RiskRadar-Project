"""
RiskRadar - Main API router.

This file mounts all sub-routers under the /api/v1 prefix.
Each sub-router handles a different resource:
  - alerts.py     -> /api/v1/alerts/*
  - summaries.py  -> /api/v1/summaries/*
  - users.py      -> /api/v1/users/*
  - system.py     -> /api/v1/health, /api/v1/scrape/trigger
"""

from fastapi import APIRouter

from api.alerts import router as alerts_router
from api.summaries import router as summaries_router
from api.users import router as users_router
from api.system import router as system_router
from api.location import router as location_router
from api.notifications import router as notifications_router
from api.forecast import router as forecast_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(alerts_router)
api_router.include_router(summaries_router)
api_router.include_router(users_router)
api_router.include_router(system_router)
api_router.include_router(location_router)
api_router.include_router(notifications_router)
api_router.include_router(forecast_router)
