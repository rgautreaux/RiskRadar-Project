"""
RiskRadar - FastAPI entry point.

This file:
  1. Creates the FastAPI app with lifespan (startup/shutdown).
  2. On startup: initializes the database and starts APScheduler.
  3. Mounts the REST API at /api/v1/* (see api/router.py).
  4. Serves the HTML frontend at / using Jinja2 templates.
  5. Serves static CSS/JS files from /static/.

HOW TO RUN:
  cd backend
  python -m uvicorn main:app --reload --port 8000

Then open http://localhost:8000 in your browser for the web frontend,
or http://localhost:8000/docs for the Swagger API docs.
"""

import logging
import socket
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db.init_db import init_database
from scrapers.scheduler import start_scheduler
from api.router import api_router
from frontend.routes import router as frontend_router
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

BASE_DIR = Path(__file__).resolve().parent


def _get_local_ip() -> str | None:
    """Best-effort detection of the machine's LAN IP for CORS."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB + start scrapers. Shutdown: stop scheduler."""
    init_database()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="RiskRadar API", version="1.0.0", lifespan=lifespan)

# --- CORS middleware -------------------------------------------------------
<<<<<<< HEAD
origins_raw = settings.CORS_ALLOWED_ORIGINS.strip()
if origins_raw == "*":
  cors_origins = ["*"]
else:
  cors_origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
  allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
=======
# Allows the React Native app and web frontend to call the API.
# Includes the machine's LAN IP so physical Expo devices on the same
# network are not blocked.  Add your production domain when deploying.
_cors_origins = [
    "http://localhost:8081",       # Expo web dev
    "http://localhost:19006",      # Expo web alt port
    "http://localhost:8000",       # Backend HTML frontend
    "http://127.0.0.1:8000",
]

_lan_ip = _get_local_ip()
if _lan_ip:
    _cors_origins.append(f"http://{_lan_ip}:8081")
    _cors_origins.append(f"http://{_lan_ip}:8000")
    _cors_origins.append(f"http://{_lan_ip}:19006")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
>>>>>>> QuiV2
)

# --- Static files (CSS, JS) -----------------------------------------------
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# --- API routes (REST JSON) ------------------------------------------------
app.include_router(api_router)

# --- Frontend routes (HTML pages) ------------------------------------------
# These must be included AFTER the API routes so /api/v1/* takes priority.
app.include_router(frontend_router)
