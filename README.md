
# Group6-Senior-Project

This repository contains the code and documentation for Group 6's Senior Project. The primary objective is to resolve environmental problems thruogh Data Analytics.

The project focuses on developing a mobile app called **RiskRadar** to help residents and travelers identify and manage potential environmental risks.

---

# Project Purpose
RiskRadar is designed to help users identify and manage potential environmental conditions and risks they may encounter whilst traveling or their day-to-day activities. The app provides features such as real-time alerts, climate data statistics, and user-friendly 5-Minute Summaries.

---

# Team Members, Roles, Responsibilities, and Contributions

| Qui                           | Back-end development, Jira                                                                 | (Contributions) |


| Noah                           | Security analyst, database                                                                  | (Contributions) |


| Celeste                           | Research analyst, front-end                                                                  | (Contributions) |


| Ben                           | Front-end/ UI development, Jira                                                                  | (Contributions) |


| Max                           | Back-end/Front-end                                                                | (Contributions) |


| Rebecca                           | Database development, Wireframes | (Contributions) |

---

# RiskRadar Backend

Environmental alert monitoring and AI-powered summarization platform.

RiskRadar scrapes real-time data from government APIs and websites (weather, air quality, wildfires, pollution, earthquakes), stores alerts in a local database, and uses LLMs to generate human-readable daily digests.

---

## Architecture Overview

```
                         +---------------------+
                         |   Web Frontend       |
                         |  (Jinja2 templates)  |
                         +----------+----------+
                                    |
                         localStorage JWT token
                              fetch() calls
                                    |
                         +----------v----------+
                         |    FastAPI Server    |
                         |     (main.py)        |
                         +----+-----+-----+----+
                              |     |     |
               +--------------+     |     +---------------+
               |                    |                     |
      +--------v-------+  +--------v--------+  +---------v--------+
      |  /api/v1/alerts |  | /api/v1/summaries|  | /api/v1/users   |
      |  (alerts.py)    |  | (summaries.py)   |  | (users.py)      |
      +--------+-------+  +--------+---------+  +---------+-------+
               |                    |                      |
               +----------+---------+-----+----------------+
                          |               |
                 +--------v--------+  +---v-------------+
                 |    SQLAlchemy    |  | auth/security.py|
                 |   ORM Layer     |  | bcrypt + JWT    |
                 +--------+--------+  +-----------------+
                          |
                 +--------v--------+
                 |   SQLite DB     |
                 | (riskradar.db)  |
                 +-----------------+
```

---

## How the Frontend Connects to the Backend

The web frontend is built with **Jinja2 HTML templates** served by FastAPI. Here is the connection flow:

```
1. User opens http://localhost:8000 -> sees login page (templates/login.html)

2. User submits login form:
   Browser JS -> POST /api/v1/users/login { email, password }
   Backend (api/users.py) -> verify_password(password, user.password_hash)
                           -> create_access_token({ sub: user.id })
                           -> returns { access_token: "eyJ...", token_type: "bearer" }
   Browser JS -> localStorage.setItem('riskradar_token', token)
              -> redirect to /dashboard

3. All subsequent API calls include the JWT:
   Browser JS -> fetch('/api/v1/alerts', {
                   headers: { 'Authorization': 'Bearer eyJ...' }
                 })
   Backend (auth/security.py) -> decode JWT -> load User from DB
                               -> return data if valid
                               -> return 401 if expired/invalid

4. If 401 received -> clear token -> redirect to login
```

### Key Files for Frontend-Backend Connection

| File | Purpose |
|------|---------|
| `templates/base.html` | Shared layout + `apiFetch()` JS helper that adds JWT to all requests |
| `templates/login.html` | Login form -> calls POST `/api/v1/users/login` |
| `templates/register.html` | Registration form -> calls POST `/api/v1/users/register` |
| `templates/dashboard.html` | Alerts view -> calls GET `/api/v1/alerts` + `/alerts/stats` |
| `templates/summaries.html` | Summary view -> calls GET/POST `/api/v1/summaries` |
| `templates/settings.html` | Settings -> calls GET `/api/v1/users/me` + PUT `/preferences` |
| `auth/security.py` | Password hashing (bcrypt) + JWT create/verify + `get_current_user` dependency |
| `config/settings.py` | JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES |
| `static/css/style.css` | All frontend styling |

---

## Scraper Pipeline

Every scraper follows the same fetch-normalize-dedup-store pipeline defined in `BaseScraper`:

```
  +------------------+
  | External Source   |    NWS API, AirNow, EPA, NASA FIRMS,
  | (API / Website)   |    USGS, config-driven sources
  +---------+--------+
            |
            v
  +---------+--------+
  | fetch_raw_data() |    Hit API or scrape website
  | Returns raw JSON  |    (httpx GET/POST, Firecrawl)
  +---------+--------+
            |
            v
  +---------+--------+
  |   normalize()    |    Map raw fields to Alert schema
  |  per raw item     |    Compute severity, extract coords
  +---------+--------+
            |
            v
  +---------+--------+
  | Deduplication     |    Check (source, source_id) unique
  | Skip if exists    |    constraint in DB
  +---------+--------+
            |
            v
  +---------+--------+
  |  Store in DB      |    INSERT new Alert rows
  |  + ScrapeLog      |    Log fetch count, duration, status
  +------------------+
```

### Three Types of Scrapers

| Type | When to Use | How to Add |
|------|-------------|------------|
| **Legacy** | Complex parsing logic | Write a Python file, register in `registry.py` |
| **GenericAPI** | Standard REST APIs | Add YAML entry to `sources.yaml` |
| **WebScraper** | Arbitrary websites | Add YAML entry to `sources.yaml` |

---

## API Endpoints

### Authentication
## MariaDB (MySQL) Schema Breakdown

RiskRadar supports MariaDB/MySQL in addition to SQLite. For scraper ingestion, the operational tables are:

- `alerts` — one row per normalized alert from any source
  - Primary key: `id`
  - Dedup key: `UNIQUE(source, source_id)`
  - Core fields: `source`, `source_id`, `alert_type`, `severity`, `title`, `description`
  - Geo/time fields: `latitude`, `longitude`, `location_name`, `event_start`, `event_end`
  - Metadata: `raw_data`, `fetched_at`, `created_at`, `updated_at`

- `scrape_log` — one row per scraper run
  - Primary key: `id`
  - Run tracking: `source`, `status`, `alerts_fetched`, `alerts_new`, `duration_ms`
  - Diagnostics: `error_message`, `started_at`, `completed_at`

- `summaries` — generated digest records from LLM output
  - Primary key: `id`
  - Core fields: `title`, `content`, `summary_type`, `alert_ids`, `region`
  - Metadata: `generated_at`, `model_used`, `token_count`, `created_at`

- `users` — profile + alert preference records
  - Primary key: `id`
  - Identity/preference fields: `email` (unique), `display_name`, `zip_code`, `alert_types`, `notify_severity`
  - Device/location fields: `device_token`, `latitude`, `longitude`
  - Metadata: `created_at`, `updated_at`

MariaDB migration used for scraper compatibility:

- `backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql`

Set DB runtime connection in `.env`:

```env
DATABASE_URL=mysql+pymysql://riskradar_user:your_password@127.0.0.1:3306/riskradar_db
```

---

## Database-Scraper Connection

Scrapers and database persistence are connected through `BaseScraper.run()`:

1. `fetch_raw_data()` pulls source data (NWS, EPA, FIRMS, AirNow, Generic API, or Web source).
2. `normalize()` maps each raw record into the `alerts` table shape.
3. Dedup checks `alerts` by `(source, source_id)`.
4. New alerts are inserted; duplicates are skipped.
5. Each run writes a `scrape_log` row with fetched/new counts, duration, and status.

This means database troubleshooting should focus on:

- schema compatibility with `alerts` and `scrape_log`
- valid `DATABASE_URL`
- scraper-specific external API response shape

---

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/users/register` | Public | Create account (bcrypt hashes password) |
| POST | `/api/v1/users/login` | Public | Authenticate -> returns JWT token |

### Alerts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/alerts` | Public | List alerts (paginated, filterable) |
| GET | `/api/v1/alerts/stats` | Public | Count by type and severity |
| GET | `/api/v1/alerts/{id}` | Public | Get single alert |

**Query params:** `alert_type`, `severity`, `source`, `limit` (default 50), `offset` (default 0)

### Summaries

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/summaries` | Public | List summaries |
| GET | `/api/v1/summaries/latest` | Public | Most recent summary |
| POST | `/api/v1/summaries/generate` | Public | Generate daily digest via LLM |

### Users (Protected - requires Bearer token)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/me` | JWT | Get current user profile |
| GET | `/api/v1/users/{id}/preferences` | JWT | Get user preferences |
| PUT | `/api/v1/users/{id}/preferences` | JWT | Update preferences |
| GET | `/api/v1/users/notifications` | JWT | Get notification settings |
| PUT | `/api/v1/users/notifications` | JWT | Update notification settings |

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | Public | Health check + DB stats |
| POST | `/api/v1/scrape/trigger` | JWT | Manually trigger all scrapers |

---

## Project Structure

```
backend/
  main.py                       # FastAPI app + lifespan (startup/shutdown)
  requirements.txt
  pytest.ini
  riskradar.db                  # SQLite database (auto-created)

  auth/                         # NEW - Authentication module
    security.py                 # bcrypt hashing, JWT create/verify, get_current_user

  api/
    router.py                   # Mounts all sub-routers under /api/v1
    alerts.py                   # GET /alerts, /alerts/stats, /alerts/{id}
    summaries.py                # GET/POST /summaries
    users.py                    # POST /register, /login, GET /me, preferences, notifications
    system.py                   # GET /health, POST /scrape/trigger

  db/
    database.py                 # SQLAlchemy engine + SessionLocal + Base
    init_db.py                  # create_all() on startup
    models.py                   # Alert, Summary, User, ScrapeLog

  config/
    settings.py                 # Pydantic BaseSettings (.env loader) - includes JWT config
    sources.yaml                # Config-driven scraper definitions

  schemas/
    alert.py                    # AlertOut, AlertStats Pydantic models
    summary.py                  # SummaryOut
    user.py                     # UserCreate, UserLogin, TokenOut, UserOut, etc.

  scrapers/
    base_scraper.py             # Abstract base: fetch -> normalize -> dedup -> store
    scheduler.py                # APScheduler job registration
    registry.py                 # Loads legacy + YAML-configured scrapers
    nws_scraper.py              # NOAA National Weather Service
    airnow_scraper.py           # EPA AirNow (air quality)
    epa_scraper.py              # EPA Envirofacts (TRI facilities)
    firms_scraper.py            # NASA FIRMS (wildfires)
    generic_api_scraper.py      # Config-driven REST API scraper
    web_scraper.py              # Firecrawl + LLM web scraper

  llm/
    summarizer.py               # Daily digest + breaking alert generation
    prompts.py                  # System/user prompt templates

  frontend/                     # NEW - HTML frontend routes
    routes.py                   # Jinja2 page routes (/, /dashboard, /summaries, /settings)

  templates/                    # NEW - Jinja2 HTML templates
    base.html                   # Shared layout + apiFetch() JS helper
    login.html                  # Login page
    register.html               # Registration page
    dashboard.html              # Alerts dashboard
    summaries.html              # AI summaries page
    settings.html               # User settings page

  static/                       # NEW - Static assets
    css/style.css               # Main stylesheet

  tests/
    conftest.py                 # Shared fixtures (in-memory DB, test client)
    test_models.py              # ORM model tests
    test_api_alerts.py          # Alert endpoint tests
    test_api_summaries.py       # Summary endpoint tests
    test_api_users.py           # User endpoint tests
    test_scrapers.py            # Scraper logic tests
    test_registry.py            # Registry loader tests
```

---

## Quick Start

### 1. Install dependencies

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate      # Linux/Mac
# ..\.venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Configure environment

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
# Then edit .env with your values
```

**Minimum required settings:**

```env
# Generate a secret: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your-random-secret-here

# For summary generation (pick one provider):
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=your-llm-api-key
```

See `.env.example` for all available settings.

### 3. Run the server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The server will:
1. Create the SQLite database (`riskradar.db`)
2. Start background scrapers on staggered intervals
3. Serve the **Web Frontend** at `http://localhost:8000`
4. Serve the **REST API** at `http://localhost:8000/api/v1/`
5. Show **Swagger docs** at `http://localhost:8000/docs`

### 4. Use the web frontend

1. Open `http://localhost:8000` in your browser
2. Click "Register here" to create an account
3. Log in with your email and password
4. Browse alerts on the dashboard, view AI summaries, update settings

### 5. Use the API directly (curl examples)

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test User", "email": "test@example.com", "password": "secret123"}'

# Login - get a JWT token
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret123"}'
# Response: { "access_token": "eyJ...", "token_type": "bearer" }

# Use the token for protected endpoints
TOKEN="eyJ..."
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# Get alerts (public)
curl http://localhost:8000/api/v1/alerts?limit=10

# Check system health
curl http://localhost:8000/api/v1/health
```

---

## Connecting a React Native / Mobile Frontend

If building a mobile app instead of using the web frontend:

1. **Base URL**: Set your API base URL to `http://<your-ip>:8000`
2. **Login**: POST to `/api/v1/users/login` with `{ email, password }`
3. **Store token**: Save the `access_token` from the response using `expo-secure-store`
4. **Attach to requests**: Add `Authorization: Bearer <token>` header to all API calls
5. **Handle 401**: If any call returns 401, clear the stored token and redirect to login

```typescript
// Example: services/api.ts
const API_BASE = 'http://192.168.1.100:8000';

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = await SecureStore.getItemAsync('jwt_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    await SecureStore.deleteItemAsync('jwt_token');
    // Navigate to login screen
  }
  return res;
}
```

---

## Adding a New Data Source

### Option A: REST API (no code needed)

Edit `config/sources.yaml` and add an entry under `api_sources`.

### Option B: Website (no code needed)

Add an entry under `web_sources` in `config/sources.yaml`.
Requires `FIRECRAWL_API_KEY` and `LLM_API_KEY` in `.env`.

### Option C: Custom scraper (Python)

1. Create `scrapers/my_scraper.py` extending `BaseScraper`
2. Register in `scrapers/registry.py`

See existing scrapers (nws, airnow, epa) for examples.

---

## Running Tests

```bash
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt

# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_api_alerts.py -v

# Run one specific test function
python -m pytest tests/test_retention.py::test_retention_archives_and_deletes_in_batches -v
```

Tests use an in-memory SQLite database and mock all external calls. No API keys needed.

### What the pytest suite covers (and why)

Pytest is used to prevent regressions across the full backend lifecycle: API behavior, ORM rules, scraper normalization, deduplication, scheduler wiring, and retention cleanup.

| File | What it tests | Why it exists |
|------|---------------|---------------|
| `backend/tests/conftest.py` | Shared fixtures (`db_session`, `test_client`, sample data) using in-memory SQLite + `TestClient` dependency overrides | Keeps tests isolated from production DB and scheduler side-effects so runs stay deterministic and fast |
| `backend/tests/test_models.py` | ORM constraints and persistence for `Alert`, `Summary`, `User`, `ScrapeLog` | Catches schema/constraint regressions early (especially unique keys and nullable behavior) |
| `backend/tests/test_api_alerts.py` | `/api/v1/alerts`, `/alerts/stats`, `/alerts/{id}` filtering, pagination, empty states, 404 behavior | Protects API contract expected by web/mobile clients |
| `backend/tests/test_api_summaries.py` | summary listing/latest endpoints and `/summaries/generate` with mocked LLM call | Verifies summary endpoints work without requiring live LLM access |
| `backend/tests/test_api_users.py` | registration and preference update endpoints, duplicate email handling, password hashing path | Ensures account and preference flows remain stable |
| `backend/tests/test_scrapers.py` | severity-mapping helpers, generic scraper field extraction/template logic, `BaseScraper.run()` dedup + log writes | Validates core normalization and dedup logic used by all sources |
| `backend/tests/test_registry.py` | YAML source loading, enabled/disabled source handling, legacy scraper registration | Confirms dynamic source configuration works and fails safely |
| `backend/tests/test_retention.py` | retention dry-run behavior, archive+delete batching, scheduler registration of nightly/weekly cleanup jobs | Protects long-term DB hygiene and cleanup automation correctness |
| `backend/tests/test_scraper_db_integration.py` | end-to-end scraper -> DB path with mocked HTTP responses for NWS/EPA/USGS | Proves real scraper classes persist alerts and scrape logs correctly |

### Additional non-pytest validation script

`backend/test_scrape_and_summarize.py` is a manual integration check script (not auto-discovered by `pytest` because it is outside `backend/tests/`).

It is useful for quickly validating:

- database initialization
- scraper execution against free/public sources
- end-to-end summary generation path

Run it with:

```bash
cd backend
python test_scrape_and_summarize.py
```

### Helpful pytest commands

```bash
# Quiet output + short tracebacks (aligned with pytest.ini defaults)
python -m pytest -q

# Run only API tests
python -m pytest tests/test_api_alerts.py tests/test_api_summaries.py tests/test_api_users.py -v

# Run only scraper + retention tests
python -m pytest tests/test_scrapers.py tests/test_scraper_db_integration.py tests/test_retention.py -v
```

### Troubleshooting DB-Scraper

Use this exact command from the project root to run the dedicated scraper/database integration tests:

```bash
cd backend
python -m pytest tests/test_scraper_db_integration.py -v --tb=short
```

What common failures usually mean:

- `OperationalError` / connection refused
  - `DATABASE_URL` is incorrect or MariaDB is not running.

- `ModuleNotFoundError: pymysql`
  - MariaDB driver is missing in environment; install backend requirements.

- `ModuleNotFoundError: passlib`
  - Authentication dependency is missing in environment; run `pip install -r backend/requirements.txt`.

- assertion failures on alert counts
  - Dedup key conflict or schema mismatch (`alerts` not aligned with model fields).

- failures writing `scrape_log`
  - `scrape_log` columns/constraints do not match expected schema.

- failures in live scrape script but test passes
  - external API/auth/network issue (integration test mocks external HTTP).

---

## Data Cleanup Scheduled Job (Retention)

RiskRadar includes a scheduled database retention job that archives old records and removes them from high-churn operational tables.

### What it is

- A background APScheduler job registered in `backend/scrapers/scheduler.py`
- Cleanup logic implemented in `backend/db/retention.py`
- Automatically started with the app lifecycle in `backend/main.py`

### What it does

When `RETENTION_ENABLED=true`, the scheduler registers two cron jobs:

- `retention_nightly` (daily at `RETENTION_NIGHTLY_HOUR_UTC:00` UTC)
  - cleans `scrape_log` records older than `RETENTION_SCRAPE_LOG_DAYS`
- `retention_weekly` (weekly on `RETENTION_WEEKLY_DAY_UTC` at `RETENTION_WEEKLY_HOUR_UTC:00` UTC)
  - cleans `alerts`, `summaries`, and `scrape_log` records based on retention-day settings

For each table, cleanup creates a `cleanup_run` record that tracks:

- rows eligible
- rows archived
- rows deleted
- estimated bytes affected
- duration and status

Records are copied to archive tables (`*_archive`) before deletion when not in dry-run mode.

### Why it helps this project

- prevents unbounded growth of alerts/log tables from continuous scraping
- keeps query performance stable for dashboard and API endpoints
- preserves historical traceability in archive tables for audits/debugging
- supports safe rollout via dry-run mode before live deletion

### Safety controls and configuration

Retention behavior is controlled entirely by environment variables:

- `RETENTION_ENABLED` (default `false`)
- `RETENTION_DRY_RUN` (default `true`)
- `RETENTION_BATCH_SIZE`
- `RETENTION_MAX_ROWS_PER_RUN`
- `RETENTION_ALERTS_DAYS`
- `RETENTION_SUMMARIES_DAYS`
- `RETENTION_SCRAPE_LOG_DAYS`
- `RETENTION_NIGHTLY_HOUR_UTC`
- `RETENTION_WEEKLY_DAY_UTC`
- `RETENTION_WEEKLY_HOUR_UTC`

Recommended rollout:

1. Enable with dry-run first (`RETENTION_ENABLED=true`, `RETENTION_DRY_RUN=true`).
2. Observe `cleanup_run` metrics for expected row counts.
3. Switch to live mode (`RETENTION_DRY_RUN=false`) after validation.

### Manual execution (ad-hoc validation)

You can run cleanup manually from the backend directory:

```bash
python -c "from db.retention import run_retention_cleanup; run_retention_cleanup('nightly')"
python -c "from db.retention import run_retention_cleanup; run_retention_cleanup('weekly')"
```


# MariaDB Migration Notes

Use `2026-03-03_mariadb_scraper_alignment.sql` to align an existing MariaDB schema with the backend ORM models used by scrapers.

**What it fixes:**

- `alerts` shape and nullability to match `db.models.Alert`
- `scrape_log` shape to match `db.models.ScrapeLog`
- `summaries.reigon` typo to `summaries.region`
- `users` shape to match `db.models.User`
- Removes constraints/indexes that block recurring scraper inserts

## Apply MariaDB Migrations

```sql
SOURCE backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql;
```

## Runtime configuration for MariaDB Migrations

Set `DATABASE_URL` in `.env` to run backend against MariaDB.

Example:

```env
DATABASE_URL=mysql+pymysql://riskradar_user:your_password@127.0.0.1:3306/riskradar_db
```

If `DATABASE_URL` is not set, backend continues using local SQLite (`DB_PATH`).

---

### MariaDB Quick Verify

After running a scraper or the integration test, use these SQL checks:

```sql
-- 1) Confirm database and table access
SELECT DATABASE() AS active_db;
SHOW TABLES LIKE 'alerts';
SHOW TABLES LIKE 'scrape_log';

-- 2) Check latest scrape runs
SELECT id, source, status, alerts_fetched, alerts_new, duration_ms, completed_at
FROM scrape_log
ORDER BY id DESC
LIMIT 10;

-- 3) Check newest alerts inserted
SELECT id, source, source_id, alert_type, severity, LEFT(title, 120) AS title
FROM alerts
ORDER BY id DESC
LIMIT 10;

-- 4) Verify dedup key behavior (should return at most 1 row per pair)
SELECT source, source_id, COUNT(*) AS c
FROM alerts
GROUP BY source, source_id
HAVING COUNT(*) > 1;
```

Expected results:

- `scrape_log` has new rows for each run with `status='success'` (or `failure` with `error_message`).
- `alerts` row count increases only for new source records.
- dedup query returns zero rows.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes** | Secret for signing JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime (default: 60) |
| `LLM_API_KEY` | For summaries | OpenAI, Anthropic, or DeepSeek API key |
| `LLM_PROVIDER` | No | `deepseek` (default), `openai`, or `anthropic` |
| `LLM_MODEL` | No | `deepseek-chat` (default) |
| `AIRNOW_API_KEY` | For air quality | AirNow API key |
| `NASA_FIRMS_MAP_KEY` | For FIRMS | NASA FIRMS MAP key |
| `FIRECRAWL_API_KEY` | For web scraping | Firecrawl API key |
| `SCRAPE_INTERVAL_MINUTES` | No | Default interval (30) |
| `RETENTION_ENABLED` | No | Enables scheduled retention cleanup jobs when `true` |
| `RETENTION_DRY_RUN` | No | If `true`, records eligible rows without deleting data |
| `RETENTION_BATCH_SIZE` | No | Number of rows processed per cleanup batch |
| `RETENTION_MAX_ROWS_PER_RUN` | No | Maximum rows processed in a single cleanup run |
| `RETENTION_ALERTS_DAYS` | No | Retention window for `alerts` table |
| `RETENTION_SUMMARIES_DAYS` | No | Retention window for `summaries` table |
| `RETENTION_SCRAPE_LOG_DAYS` | No | Retention window for `scrape_log` table |
| `RETENTION_NIGHTLY_HOUR_UTC` | No | UTC hour used by nightly retention job |
| `RETENTION_WEEKLY_DAY_UTC` | No | UTC day-of-week for weekly retention job (e.g., `sun`) |
| `RETENTION_WEEKLY_HOUR_UTC` | No | UTC hour used by weekly retention job |
| `DEFAULT_ZIP_CODE` | No | Default location ZIP (90001) |
| `DEFAULT_LAT` | No | Default latitude (34.0522) |
| `DEFAULT_LON` | No | Default longitude (-118.2437) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Authentication | bcrypt (passlib) + JWT (python-jose) |
| Frontend | Jinja2 templates + vanilla JS |
| Scheduler | APScheduler |
| HTTP Client | httpx |
| Web Scraping | Firecrawl API |
| LLM | OpenAI / Anthropic / DeepSeek |
| Validation | Pydantic |
| Config | YAML + python-dotenv |
| Testing | pytest + pytest-mock |
