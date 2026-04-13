# MariaDB Migration Notes

Use `2026-03-03_mariadb_scraper_alignment.sql` to align an existing MariaDB schema with the backend ORM models used by scrapers.
Use `2026-03-09_mariadb_retention_cleanup.sql` to add scheduled retention archive/delete support.
Use `2026-04-11_notification_channels_dispatch_log.sql` to add persisted notification channel preferences and delivery observability logging.
Use `2026-04-12_phase2_phase4_normalization_tables.sql` to create relational replacements for legacy JSON and geo dependency fields.
Use `2026-04-12_phase5_contract_retire_legacy_columns.sql` only after parity validation to remove legacy compatibility columns.

## What it fixes

- `alerts` shape and nullability to match `db.models.Alert`
- `scrape_log` shape to match `db.models.ScrapeLog`
- `summaries.reigon` typo to `summaries.region`
- `users` shape to match `db.models.User`
- Removes constraints/indexes that block recurring scraper inserts
- Legacy typo remediations for compatibility snapshots:
	- `user_prefernces` table renamed to `user_preferences`
	- `user_reads.articlle_id` renamed to `user_reads.article_id`
- Normalization remediations:
	- `summary_alerts` junction table replaces `summaries.alert_ids` JSON linkage
	- `user_alert_type_preferences` junction table replaces `users.alert_types` JSON linkage
	- `zip_geo` lookup supports normalized `users.zip_code -> coordinates`
	- `locations` + `alerts.location_id` canonicalize location naming from coordinates
	- `alert_raw_payloads` canonicalizes raw alert payload storage separate from alerts row
	- Contract-phase retirement script is available for `summaries.alert_ids`, `users.alert_types`, and `alerts.raw_data` after safety checks pass

## Apply migration

```sql
SOURCE backend/db/migrations/2026-03-03_mariadb_scraper_alignment.sql;
SOURCE backend/db/migrations/2026-03-09_mariadb_retention_cleanup.sql;
SOURCE backend/db/migrations/2026-04-11_notification_channels_dispatch_log.sql;
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

## Verification evidence (2026-04-11)

Local verification run completed after syncing local SQLite schema to current models.

- `python db/migrations/migrate_email_encryption.py`
	- `Migration complete.`
- `python db/migrations/validate_email_migration.py`
	- `users_total=0`
	- `users_plaintext_remaining=0`
	- `users_missing_encrypted=0`
	- `users_missing_hmac=0`
	- `migration_failed_or_error_logs=0` (scoped to latest batch window)
	- `batch_completed_records=1`
- `python db/migrations/monitor_migration_log.py`
	- `error_count=0`
	- `threshold=1`
	- `OK: migration error threshold not reached`
- `python -m pytest -q` (backend)
	- `159 passed, 3 skipped, 66 warnings in 19.23s`

SQLite dispatch log index checks (`EXPLAIN QUERY PLAN`) also confirmed expected index usage for:

- `WHERE alert_id = ?` via `idx_notification_dispatch_alert_id`
- `ORDER BY created_at DESC LIMIT ?` via `idx_notification_dispatch_created_at`

## Verification evidence (2026-04-12)

Local coordination verification run completed to refresh migration safety evidence.

- `python -m pytest -q backend/tests/`
	- `172 passed, 3 skipped, 66 warnings in 22.17s`
- `python -m pytest -q backend/tests/test_migrate_email_encryption.py backend/tests/test_migration_preflight.py backend/tests/test_migration_validation_monitoring.py backend/tests/test_migration_rollback_email_encryption.py`
	- `13 passed in 0.16s`
- `python backend/db/migrations/preflight.py`
	- Returned non-zero (`exit code 1`)
	- Blocking findings: missing required index/FK baseline in local DB snapshot (`blocking_issue_count=9`)
- `python backend/db/migrations/validate_email_migration.py`
	- Returned non-zero (`exit code 1`)
	- `users_total=0`, `migration_failed_or_error_logs=1`, `batch_completed_records=1`
- `python backend/db/migrations/monitor_migration_log.py`
	- `error_count=0`
	- `threshold=1`
	- `OK: migration error threshold not reached`

Coordination note:
- This evidence run is documentation-grade verification for current local state.
- Preflight/validator non-zero outcomes indicate migration baseline is not fully applied in this local snapshot and should be treated as a staging/prod readiness gate, not as a code regression.

## Local Closure Evidence (2026-04-12)

Full local closure run completed against `backend/riskradar.db` after creating a timestamped backup.

- Backup created:
	- `backend/riskradar.db.preclosure_20260412_155543.bak`
- Local DB rebuild:
	- `python -m db.init_db`
	- `Database ready: sqlite:///C:\Team6Project\backend\riskradar.db`
- Normalization and parity sequence:
	- `python db/migrations/migrate_email_encryption.py` -> `Migration complete.`
	- `python db/migrations/backfill_summary_alerts.py` -> `processed=0`
	- `python db/migrations/backfill_user_alert_type_preferences.py` -> `processed=0`
	- `python db/migrations/parity_validator_summaries_alerts.py` -> `mismatches=0`
	- `python db/migrations/parity_validator_user_alert_types.py` -> `mismatches=0`
- Readiness checks:
	- `python db/migrations/preflight.py` -> `status=ok`
	- `python db/migrations/schema_drift_check.py` -> `status=ok`
	- `MIGRATION_PREFLIGHT_STRICT=true MIGRATION_NORMALIZATION_CONTRACT_REQUIRED=true python db/migrations/safety_gate.py` -> `status=ok`
- Backend regression suite:
	- `python -m pytest -q backend/tests`
	- `185 passed, 3 skipped, 66 warnings`

Result:
- Local environment is in closure-ready state with no blocking migration or schema drift findings.
- Remaining stage closure is operational rollout work and should run the same sequence against staging MariaDB credentials.

## Staging/Production Handoff (2026-04-12)

Execution from this workspace could not run against staging/production because no staging/prod DB credentials were present in environment variables during this session (`no_staging_or_prod_db_env_detected`).

Use the same verified sequence below in staging first, then production:

1. `python db/migrations/migrate_email_encryption.py`
2. `python db/migrations/backfill_summary_alerts.py`
3. `python db/migrations/backfill_user_alert_type_preferences.py`
4. `python db/migrations/parity_validator_summaries_alerts.py`
5. `python db/migrations/parity_validator_user_alert_types.py`
6. `python db/migrations/preflight.py`
7. `python db/migrations/schema_drift_check.py`
8. `MIGRATION_PREFLIGHT_STRICT=true MIGRATION_NORMALIZATION_CONTRACT_REQUIRED=true python db/migrations/safety_gate.py`
9. `python -m pytest -q backend/tests`

Local verified baseline for comparison:
- preflight: `status=ok`
- schema drift: `status=ok`
- strict contract safety gate: `status=ok`
- backend tests: `185 passed, 3 skipped`
