# RiskRadar — Group 6 Senior Project

Environmental risk monitoring mobile app with real-time alerts, air quality data, and AI-powered summaries.

RiskRadar helps residents and travelers identify environmental risks by scraping government APIs (NWS weather, AirNow air quality, NASA wildfires, EPA pollution, USGS earthquakes), storing alerts in a database, and generating AI daily digests.

---

## April 10, 2026 Synchronization Note

- Critical backend regression coverage was expanded this session for location ingestion, local summaries, system trigger/health behavior, and user auth/notification paths.
- Full backend validation completed in this session: 107 passed, 0 failed (warnings only).
- Documentation, transcript, and progress-tracking records are synchronized around this validation state; backend/security lead sign-off remains the external non-code approval gate.

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

## Project Stages & Progress (as of Apr 10, 2026)

### Stage 1: Security & Migration
- Comprehensive User Security Plan implemented (encryption, key management, audit logging planned)
- All preparatory work (migration scripts, rollback, logging, monitoring, staging setup) completed in test/staging environments
- Documentation-driven approach ensures all changes are safe, reversible, and fully auditable

### Stage 2: Automated Data Retention & Cleanup
- Scheduled archive and deletion system keeps the database performant and compliant
- Retention jobs (nightly/weekly) archive and delete old data, with full logging and dry-run safety
- All retention logic, migrations, and tests are documented and validated

### Stage 3: End-to-End Testing & Validation
- Full backend pytest suite (87/87 passing) covers API, database, scrapers, retention logic, and user registration/login regressions
- Integration tests ensure scraper-to-database pipeline is robust and reliable
- Backend smoke verification script now completes cleanly, including config-driven scraper loading and conditional summary generation when no LLM provider is configured
- CI/local pre-push checklist ensures code quality and reproducibility

### Stage 4: Frontend UI/UX & Wireframe Accuracy
- Mobile app UI/UX plan finalized and mapped to wireframe assets
- Implementation checklist and asset mapping ensure efficient, brand-accurate styling
- All frontend components are structured for maintainability and scalability

### Stage 5: Documentation & Team Alignment
- All major sessions and developments are logged in REBECCA-TRANSCRIPT.md and GROUP_PROGRESS_LOG
- AUTHORS.md details each member's contributions and roles
- README, TODO, and top-level planning/tracking docs are kept synchronized for auditability and onboarding
- Apr 10 update: migration verification evidence from this environment was recorded (targeted migration tests passed and migration script execution completed successfully), and the documentation bundle was refreshed in lockstep
- Apr 10 update: Rebecca’s code-side implementation work is complete; the remaining dependency is backend/security lead sign-off, and the documentation bundle now reflects that boundary explicitly
- Apr 2 update: Phase 3 security implementation evidence and backend/security review-request content are now documented and ready for lead sign-off workflow
- Apr 2 update: backend pytest, frontend lint, and scraper smoke verification were rerun; the backend suite passed cleanly, frontend lint/typecheck completed cleanly, and the smoke script completed without summary-generation errors
- Apr 2 follow-up: documentation sync records were refreshed again so the latest transcript, progress, reflection, TODO, sprint tracking, QA, and AUTHORS entries remain in lockstep
- Apr 2 follow-up request: the newest transcript/progress/reflection/update pass is now recorded so the documentation audit trail reflects this session as well

---

## Major Developments & Implementation Highlights (as of Apr 10, 2026)

- All stage-specific progress notes and updates are now organized at the end of the README for clarity and auditability.
- Top-level documentation (README, TODO, AUTHORS, GROUP_PROGRESS_LOG, REBECCA-TRANSCRIPT, REFLECTION) is synchronized and audit-ready.
- Verbatim, word-for-word transcript of this session added to REBECCA-TRANSCRIPT.md in correct chronological order.
- Duplicate transcript entries removed; all entries are unique and in order.
- REFLECTION.md updated with a summary of this session, the rationale, and its impact on the project.
- AUTHORS.md updated with each member’s contributions and roles in correct chronological order.
- README.md expanded with sections on implementation, functionality, execution, and importance of major developments, all in correct chronological and stage order.
- Phase 3 migration logging + monitoring implementation is complete with focused automated validation and monitoring tests; review handoff artifact prepared for backend/security leads.
- April 2 verification pass confirmed backend pytest at 87/87, frontend lint/typecheck clean, and successful smoke execution of backend/test_scrape_and_summarize.py after registry/import and generic API extraction fixes.
- The April 2 documentation follow-up added a fresh transcript entry and refreshed all audit-facing planning/progress docs without changing the verified code state.
- The Apr 2 follow-up verification pass also refreshed the transcript/progress/reflection/TODO chain so the top-level records continue to match the validated codebase state.
- The Apr 10 documentation pass preserved the same audit trail while making Rebecca’s remaining approval gate explicit.
- The Apr 10 migration-verification sync pass recorded successful migration test/script results and propagated the session update across transcript, progress, reflection, TODO, AUTHORS, README, and sprint tracking.

---

## Implementation, Functionality, Execution, and Importance

### Implementation
- Backend: Python (FastAPI), SQLAlchemy ORM, MariaDB/SQLite
- Frontend: React Native (Expo), centralized theme token system, wireframe-accurate UI/UX
- Scrapers: Government APIs (NWS, AirNow, EPA, NASA FIRMS, USGS)
- AI Summaries: LLM APIs (DeepSeek, OpenAI, Anthropic)
- Data retention: Automated jobs for cleanup and compliance
- All major developments validated with end-to-end tests and integration coverage

### Functionality
- Real-time environmental risk alerts and air quality data for US locations
- AI-generated daily digests and summaries
- User authentication, profile management, and notification preferences
- Mobile app with branded, wireframe-accurate UI, Light/Dark Mode
- Scheduled jobs for data scraping, retention, and cleanup
- Full test suite and CI-ready validation for backend and frontend

### Execution
- All preparatory work completed in test/staging before production rollout
- Documentation-driven approach ensures all changes are safe, reversible, and auditable
- Team roles and contributions are clearly defined in AUTHORS.md
- Progress and major sessions are logged in GROUP_PROGRESS_LOG and REBECCA-TRANSCRIPT.md
- All top-level documentation is kept synchronized after each major session

### Importance
- **Security:** User Security Plan ensures data protection, auditability, and compliance
- **Performance:** Automated retention and cleanup keep the system fast and scalable
- **Reliability:** End-to-end tests and integration coverage prevent regressions and ensure correctness
- **Usability:** Wireframe-accurate UI/UX delivers a polished, user-friendly experience
- **Transparency:** Comprehensive documentation and progress logs keep the team aligned and the project audit-ready

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

Expected: `87 passed`. Tests use an in-memory database and mock all external APIs — no API keys needed.

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

---

## Scheduled Archive and Deletion System

RiskRadar includes a scheduled job system that automatically archives and deletes out-of-date alerts, summaries, and scrape logs to keep the database clean and performant.

### How It Works
- The backend scheduler registers two retention jobs:
  - **Nightly job:** Archives and deletes old scrape logs.
  - **Weekly job:** Archives and deletes old alerts and summaries, as well as scrape logs.
- Each job:
  - Moves eligible records to archive tables (e.g., `AlertArchive`, `SummaryArchive`, `ScrapeLogArchive`).
  - Deletes the original records from the main tables.
  - Logs the cleanup run in the `CleanupRun` table for auditing.
- Jobs run in batches and can be configured for dry-run mode (no data is deleted, only estimated).

### Configuration
- Retention periods, batch sizes, and schedule times are set in `config/settings.py`.
- The system is enabled/disabled via the `RETENTION_ENABLED` setting.

### Why This Matters
This system ensures that the backend database does not grow indefinitely, improves performance, and maintains historical data in archive tables for future reference.

---

For more details, see:
- [backend/scrapers/scheduler.py](backend/scrapers/scheduler.py)
- [backend/db/retention.py](backend/db/retention.py)
- [backend/db/models.py](backend/db/models.py)

---

## Project Stages & Progress

### Stage 1: Security & Migration
 - Comprehensive User Security Plan implemented (encryption, key management, audit logging planned)
 - All preparatory work (migration scripts, rollback, logging, monitoring, staging setup) completed in test/staging environments
 - Documentation-driven approach ensures all changes are safe, reversible, and fully auditable

### Stage 2: Automated Data Retention & Cleanup
 - Scheduled archive and deletion system keeps the database performant and compliant
 - Retention jobs (nightly/weekly) archive and delete old data, with full logging and dry-run safety
 - All retention logic, migrations, and tests are documented and validated

### Stage 3: End-to-End Testing & Validation
 Full backend pytest suite (87/87 passing) covers API, database, scrapers, and retention logic
 - Integration tests ensure scraper-to-database pipeline is robust and reliable
 Full backend pytest suite (87/87 passing) covers API, database, scrapers, and retention logic

### Stage 4: Frontend UI/UX & Wireframe Accuracy
 - Mobile app UI/UX plan finalized and mapped to wireframe assets
 - Implementation checklist and asset mapping ensure efficient, brand-accurate styling
 - All frontend components are structured for maintainability and scalability

### Stage 5: Documentation & Team Alignment
 - All major sessions and developments are logged in REBECCA-TRANSCRIPT.md and GROUP_PROGRESS_LOG
 - AUTHORS.md details each member's contributions and roles
 - README, TODO, and all top-level docs are kept in sync for auditability and onboarding

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

## Major Developments & Implementation Highlights (as of Mar 30, 2026)

### 1. User Security Plan & Safe Migration
- Comprehensive User Security Plan implemented (encryption, key management, audit logging planned)
- All preparatory work (migration scripts, rollback, logging, monitoring, staging setup) completed in test/staging environments
- Documentation-driven approach ensures all changes are safe, reversible, and fully auditable

### 2. Automated Data Retention & Cleanup
- Scheduled archive and deletion system keeps the database performant and compliant
- Retention jobs (nightly/weekly) archive and delete old data, with full logging and dry-run safety
- All retention logic, migrations, and tests are documented and validated

### 3. End-to-End Testing & Validation
- Full backend pytest suite (87/87 passing) covers API, database, scrapers, and retention logic
- Integration tests ensure scraper-to-database pipeline is robust and reliable
- CI/local pre-push checklist ensures code quality and reproducibility

### 4. Frontend UI/UX & Wireframe Accuracy
- Mobile app UI/UX plan finalized and mapped to wireframe assets
- Implementation checklist and asset mapping ensure efficient, brand-accurate styling
- All frontend components are structured for maintainability and scalability

### 5. Documentation & Team Alignment
- All major sessions and developments are logged in REBECCA-TRANSCRIPT.md and GROUP_PROGRESS_LOG
- AUTHORS.md details each member's contributions and roles
- README, TODO, and all top-level docs are kept in sync for auditability and onboarding

---

## Importance of Major Developments

- **Security:** User Security Plan ensures data protection, auditability, and compliance.
- **Performance:** Automated retention and cleanup keep the system fast and scalable.
- **Reliability:** End-to-end tests and integration coverage prevent regressions and ensure correctness.
- **Usability:** Wireframe-accurate UI/UX delivers a polished, user-friendly experience.
- **Transparency:** Comprehensive documentation and progress logs keep the team aligned and the project audit-ready.

---

## Why These Developments Matter

- **Security:** Ensures user data is protected, auditable, and compliant with best practices
- **Performance:** Automated cleanup and retention keep the system fast and scalable
- **Reliability:** End-to-end tests and integration coverage prevent regressions and ensure correctness
- **Usability:** Wireframe-accurate UI/UX delivers a polished, user-friendly experience
- **Transparency:** Comprehensive documentation and progress logs keep the team aligned and the project audit-ready

---
