from fastapi import APIRouter

from api.alerts import router as alerts_router
from api.summaries import router as summaries_router
from api.users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(alerts_router)
api_router.include_router(summaries_router)
api_router.include_router(users_router)
