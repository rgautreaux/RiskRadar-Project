"""
RiskRadar - Frontend HTML routes.

These routes serve Jinja2 HTML templates for the web-based frontend.
The templates call the REST API via JavaScript fetch() to get data.

Pages:
  GET /                 -> Login page (or redirects to dashboard)
  GET /register         -> Registration page
  GET /dashboard        -> Alerts dashboard (main page after login)
  GET /summaries        -> AI-generated summaries page
  GET /settings         -> User preferences/settings page

HOW IT CONNECTS:
  - Each HTML page includes JavaScript that calls /api/v1/* endpoints.
  - The JWT token is stored in localStorage after login.
  - Every API call includes the Authorization: Bearer <token> header.
  - See templates/base.html for the shared layout and JS helpers.
"""

from pathlib import Path

from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
# Workaround for Jinja2 >=3.1 cache bug: disable template cache
templates.env.cache = None

router = APIRouter(tags=["Frontend"])


@router.get("/")
def login_page(request: Request):
    """Login page — the entry point of the web frontend."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    """Registration page — create a new account."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard")
def dashboard_page(request: Request):
    """Alerts dashboard — shows all environmental alerts."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/summaries")
def summaries_page(request: Request):
    """Summaries page — shows AI-generated daily digests."""
    return templates.TemplateResponse("summaries.html", {"request": request})


@router.get("/settings")
def settings_page(request: Request):
    """Settings page — update user preferences and notifications."""
    return templates.TemplateResponse("settings.html", {"request": request})
