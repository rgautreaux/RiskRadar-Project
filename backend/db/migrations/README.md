# Migration Scripts

> **Production-ready scripts** are in this folder. Draft/planning files have been moved to `archive/` and are not for production use.

This folder will contain migration scripts for email encryption and password hashing upgrades.

- Draft scripts here before executing in production.
- Document each migration step and batch.

## Phase 3 (Migration Logging & Monitoring) Scripts

- `2026-04-12_phase1_typo_schema_fixes.sql`
  - Applies legacy schema typo remediations for MariaDB snapshots:
    - Renames `user_prefernces` -> `user_preferences`
    - Renames `user_reads.articlle_id` -> `user_reads.article_id`
  - Revalidates primary key shapes for the corrected legacy tables.

- `2026-04-12_phase1_typo_schema_fixes_rollback.sql`
  - Rollback companion for typo remediation:
    - Renames `user_preferences` -> `user_prefernces`
    - Renames `user_reads.article_id` -> `user_reads.articlle_id`
  - Restores legacy primary key shapes if rollback is required.

- `2026-04-12_phase2_phase4_normalization_tables.sql`
  - Creates normalized structures for schema remediation:
    - `summary_alerts` (replaces `summaries.alert_ids` JSON relation)
    - `user_alert_type_preferences` (replaces `users.alert_types` JSON relation)
    - `zip_geo` (zip-code to coordinate lookup)
    - `locations` + `alerts.location_id` (canonical location mapping)
    - `alert_raw_payloads` (canonical raw alert payload storage)

- `backfill_summary_alerts.py`
  - Backfills `summary_alerts` from legacy `summaries.alert_ids` JSON.

- `backfill_user_alert_type_preferences.py`
  - Backfills `user_alert_type_preferences` from legacy `users.alert_types` JSON.

- `parity_validator_summaries_alerts.py`
  - Validates relational `summary_alerts` parity against legacy `summaries.alert_ids`.

- `parity_validator_user_alert_types.py`
  - Validates relational `user_alert_type_preferences` parity against legacy `users.alert_types`.

- `2026-04-12_phase5_contract_retire_legacy_columns.sql`
  - Contract-phase migration to retire legacy compatibility columns once parity has been verified:
    - Drops `summaries.alert_ids`
    - Drops `users.alert_types`
    - Drops `alerts.raw_data`
  - Must be run only after backfill/parity/safety checks pass.

- `2026-04-12_phase5_contract_retire_legacy_columns_rollback.sql`
  - Rollback companion to restore legacy columns if Phase 5 needs reversal.

- `2026-04-12_phase0_index_hardening.sql`
  - Adds idempotent baseline indexes that preflight now requires:
    - `alerts`: `idx_alerts_source_fetched_at`, `idx_alerts_type_severity_fetched_at`
    - `summaries`: `idx_summaries_summary_type_generated_at`
    - `scrape_log`: `idx_scrape_log_source_started_at`, `idx_scrape_log_status_completed_at`
    - `cleanup_runs`: `idx_cleanup_runs_status_started_at`
    - `notification_dispatch_log`: `idx_notification_dispatch_status_created_at`
  - Uses MariaDB 10.4-compatible `information_schema.statistics` checks for idempotent index creation.

- `2026-04-12_foreign_key_integrity_hardening.sql`
  - Adds referential integrity constraints for archive lineage and notification dispatch references.
  - Adds supporting index `idx_notification_dispatch_initiated_by_user_id` when missing.
  - Enforces:
    - `alerts_archive.cleanup_run_id -> cleanup_runs.id`
    - `summaries_archive.cleanup_run_id -> cleanup_runs.id`
    - `scrape_log_archive.cleanup_run_id -> cleanup_runs.id`
    - `notification_dispatch_log.alert_id -> alerts.id`
    - `notification_dispatch_log.initiated_by_user_id -> users.id`

- `2026-04-12_mariadb_email_hmac_index_fix.sql`
  - Normalizes `users.email_hmac` to `VARCHAR(64)` for MariaDB compatibility.
  - Rebuilds `uq_users_email_hmac` idempotently to ensure reliable uniqueness checks.

- `2026-04-11_notification_channels_dispatch_log.sql`
  - Adds persistent notification channel flags on `users`:
    - `notify_push` (default `1`)
    - `notify_email` (default `0`)
    - `notify_sms` (default `0`)
  - Creates `notification_dispatch_log` table for delivery observability:
    - per-dispatch recipient totals, sent/failed counts, provider, status, and timestamp
  - Adds indexes on `notification_dispatch_log.alert_id` and `notification_dispatch_log.created_at`

- `2026-04-10_phase3_email_security_schema.sql`
  - Adds the `users.email_encrypted` and `users.email_hmac` columns required by the email migration.
  - Creates the `migration_log` table used by the Phase 3 logging, validation, and monitoring tools.

- `migrate_email_encryption.py`
  - Encrypts plaintext user emails into `email_encrypted`.
  - Computes and stores `email_hmac` for lookup uniqueness.
  - Clears legacy plaintext `email` values.
  - Writes batch lifecycle logs (`started`, `completed`, `failed`) and per-user logs (`success`, `error`) to `migration_log`.
  - Sanitizes exception text before persisting to prevent sensitive data leakage.

- `rollback_email_encryption.py`
  - Executes rollback drills by restoring `users.email` from `users.email_encrypted`.
  - Supports dry-run mode via `ROLLBACK_DRY_RUN=true`.
  - Logs batch and per-user rollback events to `migration_log`.

- `validate_email_migration.py`
  - Verifies migration invariants after a run (no plaintext emails, encrypted/HMAC fields present, no failed logs, completed batch record exists).
  - Returns non-zero exit code when checks fail.

- `monitor_migration_log.py`
  - Monitors `migration_log` for `error`/`failed` records.
  - Supports threshold-based alert behavior via `MIGRATION_ERROR_THRESHOLD`.
  - Returns non-zero exit code when threshold is reached.

- `schema_drift_check.py`
  - Compares SQLAlchemy model metadata with the current database schema.
  - Fails when required tables, columns, indexes, or foreign keys are missing.

- `safety_gate.py`
  - Runs preflight, schema drift, validation, and monitoring checks as one command.
  - Supports strict preflight via `MIGRATION_PREFLIGHT_STRICT=true|false`.
  - Supports contract enforcement via `MIGRATION_NORMALIZATION_CONTRACT_REQUIRED=true|false`.
  - Returns non-zero exit code when any safety check fails.

- `phase3_staging_evidence_template.md`
  - Fill-in worksheet for staging execution evidence collection and SQL spot-check output.
  - Intended to be attached to the Phase 3 review handoff package before approval request.

## Suggested Run Order (Staging)

1. Apply `2026-04-10_phase3_email_security_schema.sql`
2. Apply `2026-04-11_notification_channels_dispatch_log.sql`
3. Apply `2026-04-11_operational_index_hardening.sql`
4. Apply `2026-04-12_phase0_index_hardening.sql`
5. Apply `2026-04-12_foreign_key_integrity_hardening.sql`
6. Apply `2026-04-12_mariadb_email_hmac_index_fix.sql` (MariaDB only)
7. Apply `2026-04-12_phase1_typo_schema_fixes.sql` (legacy schema snapshots only)
8. Apply `2026-04-12_phase2_phase4_normalization_tables.sql`
9. `python db/migrations/backfill_summary_alerts.py`
10. `python db/migrations/backfill_user_alert_type_preferences.py`
11. `python db/migrations/parity_validator_summaries_alerts.py`
12. `python db/migrations/parity_validator_user_alert_types.py`
13. `python db/migrations/preflight.py`
14. `python db/migrations/schema_drift_check.py`
15. `python db/migrations/safety_gate.py`
16. `python db/migrations/migrate_email_encryption.py`
17. `python db/migrations/validate_email_migration.py`
18. `python db/migrations/monitor_migration_log.py`
19. (Optional contract phase) set `MIGRATION_NORMALIZATION_CONTRACT_REQUIRED=true` and run `python db/migrations/safety_gate.py`
20. (Optional contract phase) apply `2026-04-12_phase5_contract_retire_legacy_columns.sql`

Record all outputs in staging validation notes before requesting backend/security lead sign-off.

## Latest Verification Snapshot

See `backend/db/migrations/MIGRATION_NOTES.md` for the dated 2026-04-11 evidence block including migration script results, validator/monitor outputs, query-plan index checks, and full backend pytest confirmation.
