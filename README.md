# RiskRadar — Group 6 Senior Project

Environmental risk monitoring mobile app with real-time alerts, air quality data, and AI-powered summaries.

RiskRadar helps residents and travelers identify environmental risks by scraping government APIs (NWS weather, AirNow air quality, NASA wildfires, EPA pollution, USGS earthquakes), storing alerts in a database, and generating AI daily digests.

---

## Prerequisites

Before you start, make sure you have these installed on your machine:

| Tool | Version | How to check | How to install |
|------|---------|--------------|----------------|
| **Python** | 3.10+ | `py --version` | [python.org/downloads](https://www.python.org/downloads/) — check "Add to PATH" during install |
| **Node.js** | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) — LTS version recommended |
| **npm** | 9+ | `npm --version` | Comes with Node.js |
| **Git** | any | `git --version` | [git-scm.com](https://git-scm.com/) |

> **Windows users:** Use `py` instead of `python3`. If `py` doesn't work, reinstall Python from [python.org](https://www.python.org/downloads/) and check **"Add Python to PATH"** during installation.

---

## Quick Start (Run the Whole App)

### Step 1: Clone the repo

```bash
git clone https://github.com/your-org/Team6Project.git
cd Team6Project
```

### Step 2: Set up environment variables

```bash
copy .env.example .env
```

Open `.env` in a text editor and fill in at minimum:

```env
# REQUIRED — generate with: py -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=paste-your-random-secret-here

# REQUIRED for AI summaries (get a key from https://platform.deepseek.com/)
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=your-deepseek-api-key

# OPTIONAL — for air quality data (free key from https://docs.airnowapi.org/account/request/)
AIRNOW_API_KEY=your-airnow-key
```

### Step 3: Start the Backend

Open a terminal (Command Prompt or PowerShell):

```bash
cd backend
py -m pip install -r requirements.txt
py -m uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> **Leave this terminal open.** The backend must stay running.

Verify it works by opening http://localhost:8000/docs in your browser — you should see the Swagger API docs.

### Step 4: Start the Frontend (Mobile App)

Open a **second terminal**:

```bash
cd frontend\RiskRadar
npm install
npx expo start
```

Then press:
- **`w`** to open in your web browser
- **Scan the QR code** with the Expo Go app on your phone (same WiFi network)

> **Important:** The mobile app automatically detects your computer's IP address so it can reach the backend. Both devices must be on the same WiFi network.

---

## Team Members

| Name | Role |
|------|------|
| Qui | Back-end development, Jira |
| Noah | Security analyst, database |
| Celeste | Research analyst, front-end |
| Ben | Front-end / UI development, Jira |
| Max | Back-end / Front-end |
| Rebecca | Database development, Wireframes |

---

## Project Structure

```
Team6Project/
├── .env.example              # Template for environment variables
├── .env                      # Your local config (not committed)
│
├── backend/                  # Python FastAPI server
│   ├── main.py               # App entry point
│   ├── requirements.txt      # Python dependencies
│   ├── riskradar.db          # SQLite database (auto-created)
│   │
│   ├── api/                  # REST API endpoints
│   │   ├── router.py         # Mounts all routes under /api/v1
│   │   ├── alerts.py         # GET /alerts, /alerts/stats
│   │   ├── summaries.py      # GET/POST /summaries
│   │   ├── users.py          # POST /register, /login + user profile
│   │   ├── location.py       # GET /location/alerts — on-demand fetch by zip code
│   │   └── system.py         # GET /health, POST /scrape/trigger
│   │
│   ├── auth/security.py      # Password hashing (bcrypt) + JWT tokens
│   ├── config/settings.py    # All app settings loaded from .env
│   ├── config/sources.yaml   # Config-driven scraper definitions
│   │
│   ├── db/                   # Database layer
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   ├── models.py         # Alert, Summary, User, ScrapeLog tables
│   │   └── init_db.py        # Creates tables on startup
│   │
│   ├── scrapers/             # Data collection from external APIs
│   │   ├── nws_scraper.py    # NOAA weather alerts
│   │   ├── airnow_scraper.py # EPA air quality
│   │   ├── epa_scraper.py    # EPA toxic releases
│   │   ├── firms_scraper.py  # NASA wildfire data
│   │   └── scheduler.py      # Runs scrapers every 30 minutes
│   │
│   ├── llm/summarizer.py     # AI-powered daily digest generation
│   └── tests/                # pytest test suite
│
└── frontend/
    └── RiskRadar/            # React Native (Expo) mobile app
        ├── package.json      # Node.js dependencies
        ├── app/              # Screens (Expo Router file-based routing)
        │   ├── _layout.tsx   # Root layout
        │   ├── login.tsx     # Login screen
        │   ├── register.tsx  # Registration screen
        │   └── main/         # Authenticated screens
        │       ├── home.tsx          # Home — search by zip code
        │       ├── weather-report.tsx # Weather + alerts for a location
        │       ├── settings.tsx      # User preferences
        │       └── _layout.tsx       # Tab navigation
        ├── utils/api.ts      # API client (auto-adds JWT token)
        ├── constants/api.ts  # Backend URL config (auto-detects IP)
        └── contexts/auth-context.tsx  # Login/logout state management
```

---

## How the Frontend Connects to the Backend

```
┌──────────────────────────┐
│   React Native App       │
│   (Expo on phone/web)    │
└───────────┬──────────────┘
            │  HTTP requests to http://<your-ip>:8000/api/v1/...
            │  JWT token in Authorization header
            │
┌───────────▼──────────────┐
│   FastAPI Backend        │
│   (Python on your PC)    │
├──────────────────────────┤
│ /api/v1/users/login      │ → returns JWT token
│ /api/v1/users/register   │ → creates account
│ /api/v1/alerts           │ → list all alerts from DB
│ /api/v1/location/alerts  │ → fetch fresh alerts for a zip code
│ /api/v1/summaries/latest │ → latest AI summary
│ /api/v1/health           │ → server status
└───────────┬──────────────┘
            │
┌───────────▼──────────────┐
│   SQLite Database        │
│   (riskradar.db)         │
└──────────────────────────┘
```

**Key connection files:**

| File | What it does |
|------|-------------|
| `frontend/RiskRadar/constants/api.ts` | Builds the backend URL — auto-detects your PC's IP from Expo |
| `frontend/RiskRadar/utils/api.ts` | `apiFetch()` helper — adds JWT token to every request |
| `frontend/RiskRadar/contexts/auth-context.tsx` | Manages login/logout, stores JWT token |
| `backend/auth/security.py` | Verifies passwords and JWT tokens |

---

## API Endpoints

### Authentication (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Create account |
| POST | `/api/v1/users/login` | Login → returns JWT token |

### Alerts (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts (filterable by `alert_type`, `severity`, `source`) |
| GET | `/api/v1/alerts/stats` | Count alerts by type and severity |
| GET | `/api/v1/alerts/{id}` | Get a single alert |

### Location (Public — on-demand fetch)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/location/alerts?zip_code=70506` | Fetch fresh NWS + AirNow alerts for any US zip code |
| GET | `/api/v1/location/info?zip_code=70506` | Get city, state, and coordinates for a zip code |

### Summaries (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/summaries` | List all summaries |
| GET | `/api/v1/summaries/latest` | Most recent AI summary |
| POST | `/api/v1/summaries/generate` | Generate a new daily digest (requires LLM API key) |

### Users (Protected — requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| GET | `/api/v1/users/{id}/preferences` | Get user preferences |
| PUT | `/api/v1/users/{id}/preferences` | Update preferences |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check + DB stats |
| POST | `/api/v1/scrape/trigger` | Manually trigger all scrapers (JWT required) |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes** | Secret for signing login tokens |
| `LLM_API_KEY` | For summaries | DeepSeek, OpenAI, or Anthropic API key |
| `LLM_PROVIDER` | No | `deepseek` (default), `openai`, or `anthropic` |
| `AIRNOW_API_KEY` | For air quality | Free key from [airnowapi.org](https://docs.airnowapi.org/account/request/) |
| `NASA_FIRMS_MAP_KEY` | For wildfires | Key from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/area/) |
| `FIRECRAWL_API_KEY` | For web scraping | Key from [firecrawl.dev](https://firecrawl.dev) |
| `DEFAULT_ZIP_CODE` | No | Default location ZIP (default: 90001) |

---

## Running Tests

```bash
cd backend
py -m pip install -r requirements.txt
py -m pytest -q --tb=short
```

Expected: `78 passed`. Tests use an in-memory database and mock all external APIs — no API keys needed.

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `'py' is not recognized` | Install Python from [python.org](https://www.python.org/downloads/), check "Add to PATH" |
| `'uvicorn' is not recognized` | Use `py -m uvicorn` instead of `uvicorn` directly |
| Backend says `402 Insufficient Balance` | Your LLM API key (DeepSeek) has no credits — add funds or skip summary generation |
| Weather report shows wrong location | Make sure you're entering a valid 5-digit US zip code |
| Frontend can't connect to backend | Both devices must be on the same WiFi; backend must be running with `--host 0.0.0.0` |
| `ModuleNotFoundError` | Run `py -m pip install -r requirements.txt` in the backend folder |
| Expo QR code won't scan | Press `w` to test on web first; make sure Expo Go app is installed on phone |
| Registration fails silently | Check the backend terminal for error messages |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile App | React Native + Expo Router |
| Backend API | Python FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Authentication | bcrypt + JWT tokens |
| Data Sources | NWS, AirNow, EPA, NASA FIRMS, USGS |
| AI Summaries | DeepSeek / OpenAI / Anthropic |
| Background Jobs | APScheduler |
| Web Scraping | Firecrawl |
