"""RiskRadar — FastAPI entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.init_db import init_database
from scrapers.scheduler import start_scheduler
from api.router import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    scheduler = start_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()


app = FastAPI(title="RiskRadar API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"name": "RiskRadar API", "version": "1.0.0", "status": "running"}
