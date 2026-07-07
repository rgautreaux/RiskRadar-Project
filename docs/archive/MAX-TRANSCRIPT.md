# Max — Project Change Log

## March 17, 2026

### Fixed: `summaries` table missing AUTO_INCREMENT

**Files changed:** `backend/db/migrations/2026-03-18_summaries_auto_increment.sql`

**Problem:** The `summaries` table's `id` column was defined without `AUTO_INCREMENT` in both the original `riskradar_db.sql` schema and the 2026-03-03 migration (which fixed `alerts`, `scrape_log`, and `users` but missed `summaries`). Every new summary insert defaulted `id` to `0`, causing `IntegrityError: Duplicate entry '0' for key 'PRIMARY'` after the first summary was created.

**Fix:** Created a migration that reassigns the existing `id=0` row and adds `AUTO_INCREMENT` to `summaries.id`. Applied the migration to the live database.

---

### Added: Location-based local summary generation endpoint

**Files changed:** `backend/api/summaries.py`, `backend/llm/summarizer.py`

**Problem:** The `/generate/local` endpoint was a duplicate of `/generate` — it generated a global daily digest with no location filtering, ignoring the user's zip code.

**Fix:** Refactored `POST /api/v1/summaries/generate/local` to accept a `zip_code` query parameter. It now resolves the zip code to coordinates, fetches NWS and AirNow alerts for that location, stores them in the database, and calls a new `Summarizer.generate_local_digest()` method that produces a location-specific summary with `summary_type="local"` and `region` set to the city/state/zip.

---

### Added: Latest local summary retrieval endpoint

**Files changed:** `backend/api/summaries.py`

**Problem:** There was no way to retrieve the most recent local summary for a specific zip code without generating a new one.

**Fix:** Added `GET /api/v1/summaries/latest/local?zip_code=XXXXX` which returns the most recent summary where `summary_type` is `"local"` and the `region` contains the given zip code.

---

### Fixed: Frontend using wrong HTTP method for summary generation

**File changed:** `frontend/RiskRadar/app/main/weather-report.tsx`

**Problem:** The frontend called `/summaries/generate` with a GET request, but the backend endpoint is defined as POST, resulting in `405 Method Not Allowed`.

**Fix:** Updated the `apiFetch` call to use `{ method: 'POST' }` and pointed it to the new `/summaries/generate/local?zip_code=...` endpoint.

---

## March 18, 2026

### Fixed: Duplicate alert crash in location endpoint

**File changed:** `backend/api/location.py`

**Problem:** The `/api/v1/location/alerts` endpoint threw an unhandled `IntegrityError` when fetching alerts for a zip code. This occurred because of a race condition — the endpoint checks for existing alerts before inserting, but between the check and the `db.commit()`, another request or the background scraper could insert the same alert, violating the `uq_source_alert` unique constraint.

**Fix:** Added an `IntegrityError` catch around the commit. On conflict, the transaction is rolled back and the alerts are re-fetched from the database, so the endpoint returns the correct data instead of crashing.

---

### Fixed: Weather report useEffect fetching misaligned data

**File changed:** `frontend/RiskRadar/app/main/weather-report.tsx`

**Problem:** The `useEffect` in the weather report screen had two bugs. First, the initial summary fetch promise was commented out, shifting all `Promise.all` indices — `summaryData` received location info, `locInfo` received alerts, and `alertsData` received the generate result, causing the UI to display wrong data or crash. Second, the summary generation POST and the subsequent summary fetch ran in parallel, so the fetch would return stale or missing data since generation hadn't completed yet.

**Fix:** Removed the broken generic promises array. Location info, alerts, and summary generation now run in a single `Promise.all` with correct destructuring. The latest summary fetch runs *after* `Promise.all` resolves, so it picks up the freshly generated summary.
