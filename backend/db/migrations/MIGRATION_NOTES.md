# MariaDB Migration Notes

Use `2026-03-03_mariadb_scraper_alignment.sql` to align an existing MariaDB schema with the backend ORM models used by scrapers.
Use `2026-03-09_mariadb_retention_cleanup.sql` to add scheduled retention archive/delete support.

## What it fixes

- `alerts` shape and nullability to match `db.models.Alert`
- `scrape_log` shape to match `db.models.ScrapeLog`
- `summaries.reigon` typo to `summaries.region`
- `users` shape to match `db.models.User`
- Removes constraints/indexes that block recurring scraper inserts

## Apply migration

```sql
SOURCE backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql;
SOURCE backend/db/migrations/2026-03-09_mariadb_retention_cleanup.sql;
```

## Retention cleanup runtime settings

Set retention flags in `.env` (or environment variables) before enabling jobs:

```env
RETENTION_ENABLED=true
RETENTION_DRY_RUN=true
RETENTION_BATCH_SIZE=500
RETENTION_MAX_ROWS_PER_RUN=5000
RETENTION_ALERTS_DAYS=365
RETENTION_SUMMARIES_DAYS=365
RETENTION_SCRAPE_LOG_DAYS=90
RETENTION_NIGHTLY_HOUR_UTC=3
RETENTION_WEEKLY_DAY_UTC=sun
RETENTION_WEEKLY_HOUR_UTC=4
```

Recommended first run: keep `RETENTION_DRY_RUN=true` and inspect `cleanup_runs` before enabling deletes.

## Runtime configuration

Set `DATABASE_URL` in `.env` to run backend against MariaDB.

Example:

```env
DATABASE_URL=mysql+pymysql://riskradar_user:your_password@127.0.0.1:3306/riskradar_db
```

If `DATABASE_URL` is not set, backend continues using local SQLite (`DB_PATH`).
