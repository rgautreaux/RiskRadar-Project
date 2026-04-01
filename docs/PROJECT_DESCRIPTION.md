# Documentation Synchronization Note (Mar 23, 2026)

This document is in sync with README.md, GROUP_PROGRESS_LOG, AUTHORS.md, and UI_UX_STYLING_PLAN.md as of Mar 23, 2026. All project description, functionality, and importance sections reflect the current project state and major developments.

# RiskRadar Description

---

## APIs

### 1. OpenAI / Anthropic API

**Description**: OpenAI provides large language model APIs (e.g., GPT-4o-mini) for natural language understanding and text generation. Anthropic provides the Claude model family as an alternative.

**Usage**: In RiskRadar, the LLM API generates daily digest summaries and breaking alert analyses from collected environmental alerts. The provider is configurable via `LLM_PROVIDER` environment variable (`openai` or `anthropic`).

### 2. Firecrawl API

**Description**: Firecrawl is a web scraping and crawling service that turns websites into clean, structured, LLM-ready data without requiring manual selector configuration.

**Usage**: In RiskRadar, it powers the `WebScraper` class, which scrapes arbitrary websites defined in `sources.yaml` and uses an LLM to extract structured alert data from the scraped content.

### 3. National Weather Service (NWS) API

**Description**: The NOAA National Weather Service API provides weather forecasts, alerts, and observations for the United States.

**Usage**: In RiskRadar, the `NWSScraper` fetches active weather alerts and normalizes them into the standard Alert schema.

### 4. AirNow API

**Description**: The EPA AirNow API provides real-time air quality index (AQI) data and forecasts.

**Usage**: In RiskRadar, the `AirNowScraper` fetches air quality observations and maps AQI values to severity levels.

### 5. EPA Envirofacts API

**Description**: The EPA Envirofacts API provides access to environmental data including Toxic Release Inventory (TRI) facility information.

**Usage**: In RiskRadar, the `EPAScraper` fetches TRI facility data to alert users about nearby pollution sources.

### 6. NASA FIRMS API

**Description**: The NASA Fire Information for Resource Management System (FIRMS) API provides near real-time active fire data from satellite observations.

**Usage**: In RiskRadar, the `FIRMSScraper` fetches active wildfire hotspot data. Requires a `NASA_FIRMS_MAP_KEY`.

---

## Languages & Frameworks

### 1. Python

**Description**: Python is used as the primary back-end language.

**Usage**: In RiskRadar, Python handles the FastAPI REST server, web scraping orchestration, data processing pipelines, AI-driven summarization, and interaction with external APIs.

### 2. FastAPI

**Description**: FastAPI is a modern, high-performance Python web framework for building APIs, with automatic OpenAPI documentation and Pydantic validation.

**Usage**: In RiskRadar, FastAPI serves the REST API endpoints for alerts, summaries, and users. It runs on Uvicorn and provides interactive API docs at `/docs`.

### 3. React Native (Expo)

**Description**: React Native is a framework for building native mobile apps using React. Expo provides a managed workflow with pre-configured native modules and streamlined build tooling.

**Usage**: In RiskRadar, it is used to build the cross-platform mobile application from a single TypeScript codebase, targeting both iOS and Android.

### 4. TypeScript

**Description**: TypeScript is a typed superset of JavaScript that compiles to plain JavaScript, providing type safety and better developer tooling.

**Usage**: In RiskRadar, TypeScript is used for the React Native frontend codebase.

---

## Database

### MySQL (MariaDB) + SQLAlchemy

**Description**: MySQL is an open-source relational database management system. RiskRadar uses MariaDB 10.4, a MySQL-compatible fork, as its primary data store. SQLAlchemy is a Python SQL toolkit and ORM that provides a high-level interface for database operations.

**Usage**: In RiskRadar, MariaDB hosts the `riskradar_db` database, persisting users, articles, alerts, sources, scrape logs, AI-generated summaries, notification settings, and user preferences across 13 interconnected tables. SQLAlchemy manages the ORM models, database sessions, and query building. During local development, phpMyAdmin (via XAMPP) is available for database administration.

For full schema documentation, see [DATA_MODEL.md](DATA_MODEL.md).

---

## Key Libraries

### httpx

**Description**: httpx is a modern, async-capable HTTP client for Python.

**Usage**: In RiskRadar, httpx is used by all scrapers to make HTTP requests to external APIs.

### APScheduler

**Description**: APScheduler (Advanced Python Scheduler) is a Python library for scheduling jobs to run at specified intervals.

**Usage**: In RiskRadar, APScheduler runs scrapers on staggered intervals (e.g., every 30 minutes) to avoid API rate limits. Jobs are registered at server startup.

### Pydantic

**Description**: Pydantic provides data validation using Python type annotations.

**Usage**: In RiskRadar, Pydantic defines request/response schemas for the API and loads configuration from environment variables via `BaseSettings`.

---

## IDEs

### 1. Android Studio

**Description**: Android Studio is Google's official IDE for Android development, providing an emulator for testing mobile applications.

**Usage**: In RiskRadar, it is used for testing the Expo-based React Native build on the Android Emulator.

---

## CLIs

### 1. Expo CLI

**Description**: Expo is an open-source platform and CLI for building universal React Native applications.

**Usage**: In RiskRadar, it is used to develop, build, and deploy the cross-platform mobile application.