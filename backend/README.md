# RiskRadar Backend

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

## Backend Component Overview

### 1. `main.py`
- **Purpose:** Entry point for the FastAPI backend.
- **How it works:** Initializes the database, starts the scheduler, mounts API and frontend routes, serves static files.
- **Contribution:** Centralizes app startup, connects all backend modules, and exposes both API and web frontend.

### 2. `api/`
- **Purpose:** REST API endpoints for alerts, summaries, users, system health, and location-based data.
- **How it works:** Each file defines a FastAPI router for a resource (e.g., `alerts.py` for alert endpoints).
- **Contribution:** Provides all client-facing backend functionality, including data retrieval, user management, and system operations.

### 3. `auth/`
- **Purpose:** Handles authentication and security.
- **How it works:** Implements password hashing (bcrypt), JWT token creation/verification, and user authentication.
- **Contribution:** Secures user accounts and API access, enabling protected routes and user-specific data.

### 4. `config/`
- **Purpose:** Centralized configuration for app settings and scraper sources.
- **How it works:** Loads settings from `.env` and YAML files, making them available throughout the backend.
- **Contribution:** Simplifies environment setup and allows flexible configuration for scrapers and retention jobs.

### 5. `db/`
- **Purpose:** Database layer for models, session management, and migrations.
- **How it works:** Uses SQLAlchemy for ORM models (`Alert`, `Summary`, `User`, `ScrapeLog`), session creation, and table initialization.
- **Contribution:** Manages persistent storage, data integrity, and schema evolution.

### 6. `scrapers/`
- **Purpose:** Collects data from external APIs (NWS, AirNow, EPA, NASA).
- **How it works:** Each scraper implements a data fetcher for a specific source; the scheduler runs them at intervals.
- **Contribution:** Powers real-time environmental risk monitoring by ingesting fresh data.

### 7. `llm/`
- **Purpose:** AI-powered summarization of alerts and daily digests.
- **How it works:** Calls LLM providers (DeepSeek, OpenAI) to generate summaries using custom prompts.
- **Contribution:** Adds value by providing readable, actionable summaries for users.

### 8. `schemas/`
- **Purpose:** Pydantic models for API input/output validation.
- **How it works:** Defines data shapes for alerts, summaries, and users, ensuring consistent API responses.
- **Contribution:** Enforces data correctness and simplifies serialization/deserialization.

### 9. `static/` and `templates/`
- **Purpose:** Serves static assets and HTML templates for the web frontend.
- **How it works:** FastAPI mounts these directories for CSS, JS, and Jinja2 templates.
- **Contribution:** Enables a web-based dashboard and user interface.

### 10. `tests/`
- **Purpose:** Automated test suite using pytest.
- **How it works:** Contains unit and integration tests for all backend modules.
- **Contribution:** Ensures reliability, correctness, and safe development.

---

**How These Components Work Together:**
The backend orchestrates data collection, storage, summarization, and API delivery. Scrapers fetch data, which is stored in the database. The LLM module generates summaries. The API exposes this data to the frontend and external clients, while authentication secures user access. Scheduled jobs archive and clean up old data, keeping the system performant and maintainable.

For more details, see:
- [backend/scrapers/scheduler.py](backend/scrapers/scheduler.py)
- [backend/db/retention.py](backend/db/retention.py)
- [backend/db/models.py](backend/db/models.py)
