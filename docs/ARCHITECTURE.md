# Documentation Synchronization Note (Mar 23, 2026)

This document is in sync with README.md, GROUP_PROGRESS_LOG, AUTHORS.md, and UI_UX_STYLING_PLAN.md as of Mar 23, 2026. All architecture, data flow, and implementation details reflect the current project state and major developments.

# RiskRadar Architecture

---

## System Overview

RiskRadar follows a client-server architecture with a FastAPI backend, MySQL (MariaDB) database, and a React Native (Expo) mobile frontend.

```
                         +---------------------+
                         |   Frontend / App     |
                         |  (React Native/Expo) |
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
                 | MySQL (MariaDB) |
                 | (riskradar_db)  |
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

## Data Flow

1. **Scraping**: The Python backend uses **httpx** for API calls and **Firecrawl** for web scraping, running on a schedule via **APScheduler**.
2. **Normalization**: Each scraper normalizes raw data into a standard Alert schema, computes severity, and extracts coordinates.
3. **Deduplication**: Alerts are deduplicated by `(source, source_id)` unique constraint before insertion.
4. **Storage**: Processed data is persisted in **MySQL (MariaDB)** via **SQLAlchemy ORM** (`riskradar_db`).
5. **Analysis**: The **OpenAI** or **Anthropic** LLM API generates daily digest summaries from recent alerts.
6. **Presentation**: The **React Native (Expo)** mobile app fetches data from the FastAPI REST API.

---

## Database Architecture

RiskRadar uses a MariaDB 10.4 relational database (`riskradar_db`) consisting of 13 tables organized into four functional groups: **Content**, **Users**, **Alerts & AI**, and **Operations**, managed via SQLAlchemy ORM.

For full schema documentation including table definitions, entity relationships, and normalization analysis, see [DATA_MODEL.md](DATA_MODEL.md).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI + Uvicorn |
| Database | MySQL (MariaDB 10.4) + SQLAlchemy ORM |
| Scheduler | APScheduler |
| HTTP Client | httpx |
| Web Scraping | Firecrawl API |
| LLM | OpenAI / Anthropic |
| Validation | Pydantic |
| Config | YAML + python-dotenv |
| Testing | pytest + pytest-mock |
| Frontend | React Native (Expo) |
