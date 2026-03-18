# RiskRadar API Specification

---

## Base URL

```
http://localhost:8000
```

Interactive API docs available at `http://localhost:8000/docs` (Swagger UI).

---

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API name, version, status |

---

## Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/alerts` | List alerts (paginated, filterable) |
| GET | `/api/v1/alerts/stats` | Count by type and severity |
| GET | `/api/v1/alerts/{id}` | Get single alert |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alert_type` | `string` | — | Filter by alert type (e.g., `weather`, `air_quality`, `wildfire`, `pollution`, `earthquake`) |
| `severity` | `string` | — | Filter by severity (e.g., `low`, `moderate`, `high`, `extreme`) |
| `source` | `string` | — | Filter by data source (e.g., `nws`, `airnow`, `epa`, `firms`, `usgs`) |
| `limit` | `integer` | 50 | Maximum number of results |
| `offset` | `integer` | 0 | Pagination offset |

---

## Summaries

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/summaries` | List summaries |
| GET | `/api/v1/summaries/latest` | Most recent summary |
| POST | `/api/v1/summaries/generate` | Generate daily digest via LLM |

### POST `/api/v1/summaries/generate`

Triggers LLM-based summary generation from alerts in the last 24 hours. Requires `LLM_API_KEY` to be configured.

---

## Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Create account |
| PUT | `/api/v1/users/{id}/preferences` | Update preferences |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_API_KEY` | For summaries | — | OpenAI or Anthropic API key |
| `LLM_PROVIDER` | No | `openai` | `openai` or `anthropic` |
| `LLM_MODEL` | No | `gpt-4o-mini` | LLM model name |
| `NASA_FIRMS_MAP_KEY` | For FIRMS | — | NASA FIRMS MAP key |
| `FIRECRAWL_API_KEY` | For web scraping | — | Firecrawl API key |
| `SCRAPE_INTERVAL_MINUTES` | No | `30` | Default scrape interval |
| `DEFAULT_ZIP_CODE` | No | `90001` | Default location ZIP |
| `DEFAULT_LAT` | No | `34.0522` | Default latitude |
| `DEFAULT_LON` | No | `-118.2437` | Default longitude |

---

## Data Sources

| Source | Scraper | Alert Type | Interval | Requires |
|--------|---------|------------|----------|----------|
| NOAA National Weather Service | `NWSScraper` | `weather` | 30 min | — |
| EPA AirNow | `AirNowScraper` | `air_quality` | 30 min | — |
| EPA Envirofacts (TRI) | `EPAScraper` | `pollution` | 60 min | — |
| NASA FIRMS | `FIRMSScraper` | `wildfire` | 30 min | `NASA_FIRMS_MAP_KEY` |
| USGS Earthquakes | `GenericAPIScraper` | `earthquake` | 30 min | — |
| Config-driven APIs | `GenericAPIScraper` | configurable | configurable | — |
| Config-driven websites | `WebScraper` | configurable | configurable | `FIRECRAWL_API_KEY` + `LLM_API_KEY` |

---

## Adding Data Sources

### Option A: REST API (YAML config, no code)

Add an entry to `config/sources.yaml` under `api_sources`.

### Option B: Website (YAML config, no code)

Add an entry to `config/sources.yaml` under `web_sources`. Requires Firecrawl and LLM API keys.

### Option C: Custom Python scraper

1. Create a new scraper class extending `BaseScraper` in `scrapers/`
2. Implement `fetch_raw_data()` and `normalize()` methods
3. Register in `scrapers/registry.py`

---

## Project Structure

```
backend/
  main.py                       # FastAPI app + lifespan (startup/shutdown)
  requirements.txt
  pytest.ini
  riskradar_db.sql              # MySQL/MariaDB schema (see root riskradar_db.sql)

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

## Running the Server

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate   # or ..\.venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

## Running Tests

```bash
cd backend
python -m pytest -v
```

Tests use a test database and mock all external calls. No API keys needed.
