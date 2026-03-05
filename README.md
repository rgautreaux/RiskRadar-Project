
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
                         |   Frontend / App     |
                         +----------+----------+
                                    |
                              HTTP REST
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
               +----------+---------+----------------------+
                          |
                 +--------v--------+
                 |    SQLAlchemy    |
                 |   ORM Layer     |
                 +--------+--------+
                          |
                 +--------v--------+
                 |   SQLite DB     |
                 | (riskradar.db)  |
                 +-----------------+
```

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

```
                       BaseScraper (Abstract)
                              |
          +-------------------+-------------------+
          |                   |                   |
   Legacy Scrapers     GenericAPIScraper      WebScraper
   (Python code)       (YAML config)       (Firecrawl + LLM)
          |                   |                   |
   +------+------+     sources.yaml         sources.yaml
   |  |   |   |  |     api_sources:         web_sources:
  NWS Air EPA FIRMS    - usgs_earthquakes   - cal_fire_news
                       - (add more here)    - (add more here)
```

| Type | When to Use | How to Add |
|------|-------------|------------|
| **Legacy** | Complex parsing logic | Write a Python file, register in `registry.py` |
| **GenericAPI** | Standard REST APIs | Add YAML entry to `sources.yaml` |
| **WebScraper** | Arbitrary websites | Add YAML entry to `sources.yaml` |

---

## Scheduler

APScheduler runs scrapers on staggered intervals to avoid API rate limits:

```
Time ──────────────────────────────────────────────>
  t+0m   t+1m   t+3m   t+5m   t+7m
  |      |      |      |      |
  NWS    AirNow EPA    FIRMS  USGS      (first run)
  |      |      |      |      |
  every  every  every  every  every     (interval)
  30m    30m    60m    30m    30m
```

---

## Summary Generation Flow

```
  +------------------+
  | POST /summaries  |
  |   /generate      |
  +--------+---------+
           |
           v
  +--------+---------+
  | Query alerts     |    Last 24 hours from DB
  | from last 24h    |
  +--------+---------+
           |
           v
  +--------+---------+
  | Format as JSON   |    alert_type, severity, title,
  | for LLM prompt   |    description, location
  +--------+---------+
           |
           v
  +--------+---------+
  | LLM API Call     |    OpenAI (gpt-4o-mini) or
  | (summarizer.py)  |    Anthropic (claude)
  +--------+---------+
           |
           v
  +--------+---------+
  | Markdown Digest  |    Executive Summary
  | with sections    |    + Weather / Air / Fire / Pollution
  +--------+---------+
           |
           v
  +--------+---------+
  | Store Summary    |    title, content, alert_ids,
  | in DB            |    model_used, token_count
  +------------------+
```

---

## Database Schema

```
+------------------+       +------------------+
|     alerts       |       |    summaries     |
+------------------+       +------------------+
| id          PK   |  ref  | id          PK   |
| source           | <---- | alert_ids (JSON) |
| source_id        |       | title            |
| alert_type       |       | content (md)     |
| severity         |       | summary_type     |
| title            |       | region           |
| description      |       | generated_at     |
| latitude         |       | model_used       |
| longitude        |       | token_count      |
| location_name    |       | created_at       |
| event_start      |       +------------------+
| event_end        |
| raw_data (JSON)  |       +------------------+
| fetched_at       |       |     users        |
| created_at       |       +------------------+
| updated_at       |       | id          PK   |
+------------------+       | display_name     |
  UNIQUE(source,           | email  UNIQUE    |
   source_id)              | password_hash    |
                           | zip_code         |
+------------------+       | latitude         |
|   scrape_log     |       | longitude        |
+------------------+       | alert_types(JSON)|
| id          PK   |       | notify_severity  |
| source           |       | device_token     |
| status           |       | created_at       |
| alerts_fetched   |       | updated_at       |
| alerts_new       |       +------------------+
| error_message    |
| duration_ms      |
| started_at       |
| completed_at     |
+------------------+
```

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

## API Endpoints

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts (paginated, filterable) |
| GET | `/api/v1/alerts/stats` | Count by type and severity |
| GET | `/api/v1/alerts/{id}` | Get single alert |

**Query params:** `alert_type`, `severity`, `source`, `limit` (default 50), `offset` (default 0)

### Summaries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/summaries` | List summaries |
| GET | `/api/v1/summaries/latest` | Most recent summary |
| POST | `/api/v1/summaries/generate` | Generate daily digest via LLM |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Create account |
| PUT | `/api/v1/users/{id}/preferences` | Update preferences |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API name, version, status |

---

## Project Structure

```
backend/
  main.py                       # FastAPI app + lifespan (startup/shutdown)
  requirements.txt
  pytest.ini
  riskradar.db                  # SQLite database (auto-created)

  api/
    router.py                   # Mounts all sub-routers under /api/v1
    alerts.py                   # GET /alerts, /alerts/stats, /alerts/{id}
    summaries.py                # GET/POST /summaries
    users.py                    # POST /register, PUT /preferences

  db/
    database.py                 # SQLAlchemy engine + SessionLocal + Base
    init_db.py                  # create_all() on startup
    models.py                   # Alert, Summary, User, ScrapeLog

  config/
    settings.py                 # Pydantic BaseSettings (.env loader)
    sources.yaml                # Config-driven scraper definitions

  schemas/
    alert.py                    # AlertOut, AlertStats Pydantic models
    summary.py                  # SummaryOut, SummaryGenerate
    user.py                     # UserCreate, UserPrefsUpdate, UserOut

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
**For Mac**:
```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

**For Windows (Powershell)**:
```bash
cd backend
python -m venv ../.venv
source ../.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in `backend/`:

```env
# Optional - only needed for specific scrapers
NASA_FIRMS_MAP_KEY=your_nasa_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Required for summary generation
LLM_API_KEY=your_llm_key
LLM_PROVIDER=llm_provider
LLM_MODEL=llm_model
```

### 3. Run the server

```bash
python -m uvicorn main:app --reload --port 8000
```

The server will:
1. Create the SQLite database (`riskradar.db`)
2. Start background scrapers on staggered intervals
3. Serve the REST API at `http://localhost:8000`
4. Show interactive docs at `http://localhost:8000/docs`

---

## Adding a New Data Source

### Option A: REST API (no code needed)

Edit `config/sources.yaml`:

```yaml
api_sources:
  - name: "my_new_source"
    enabled: true
    alert_type: "weather"
    url: "https://api.example.com/data"
    method: "GET"
    interval_minutes: 30
    request:
      params:
        format: "json"
      headers: {}
    auth:
      type: "none"           # or query_param, header, bearer
    response:
      format: "json"
      items_path: "results"  # dot-path to array of items
    field_mapping:
      source_id: "id"
      title: "name"
      description: "details"
      latitude: "location.lat"
      longitude: "location.lng"
    severity:
      type: "fixed"
      value: "moderate"
```

### Option B: Website (no code needed)

```yaml
web_sources:
  - name: "local_news_alerts"
    enabled: true
    alert_type: "wildfire"
    url: "https://news.example.com/fire-alerts"
    interval_minutes: 60
```

Requires `FIRECRAWL_API_KEY` and `LLM_API_KEY` in `.env`.

### Option C: Custom scraper (Python)

1. Create `scrapers/my_scraper.py`:
```python
from scrapers.base_scraper import BaseScraper

class MyScraper(BaseScraper):
    source_name = "my_source"
    alert_type = "custom"

    def fetch_raw_data(self):
        # Hit your API, return list of dicts
        return [...]

    def normalize(self, raw):
        # Map raw dict to Alert fields
        return {
            "source": self.source_name,
            "source_id": raw["id"],
            "alert_type": self.alert_type,
            "severity": "moderate",
            "title": raw["title"],
            ...
        }
```

2. Register in `scrapers/registry.py`:
```python
LEGACY_SCRAPERS.append({
    "factory": lambda: MyScraper(),
    "id": "my_source",
    "interval_minutes": 30,
    "stagger_offset_minutes": 10,
    "requires_env": None,
})
```

---

## Running Tests

```bash
cd backend
source ../.venv/bin/activate
pip install pytest pytest-mock

# Run all 73 tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_api_alerts.py -v

# Run specific test class
python -m pytest tests/test_scrapers.py::TestAqiToSeverity -v
```

Tests use an in-memory SQLite database and mock all external calls. No API keys needed.

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

- assertion failures on alert counts
  - Dedup key conflict or schema mismatch (`alerts` not aligned with model fields).

- failures writing `scrape_log`
  - `scrape_log` columns/constraints do not match expected schema.

- failures in live scrape script but test passes
  - external API/auth/network issue (integration test mocks external HTTP).


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
| `LLM_API_KEY` | For summaries | OpenAI or Anthropic API key |
| `LLM_PROVIDER` | No | `openai` (default) or `anthropic` |
| `LLM_MODEL` | No | `gpt-4o-mini` (default) |
| `NASA_FIRMS_MAP_KEY` | For FIRMS | NASA FIRMS MAP key |
| `FIRECRAWL_API_KEY` | For web scraping | Firecrawl API key |
| `SCRAPE_INTERVAL_MINUTES` | No | Default interval (30) |
| `DEFAULT_ZIP_CODE` | No | Default location ZIP (90001) |
| `DEFAULT_LAT` | No | Default latitude (34.0522) |
| `DEFAULT_LON` | No | Default longitude (-118.2437) |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Scheduler | APScheduler |
| HTTP Client | httpx |
| Web Scraping | Firecrawl API |
| LLM | OpenAI / Anthropic |
| Validation | Pydantic |
| Config | YAML + python-dotenv |
| Testing | pytest + pytest-mock |
