# Migration Scripts

This folder will contain migration scripts for email encryption and password hashing upgrades.

- Draft scripts here before executing in production.
- Document each migration step and batch.

## Phase 3 (Migration Logging & Monitoring) Scripts

- `migrate_email_encryption.py`
	- Encrypts plaintext user emails into `email_encrypted`.
	- Computes and stores `email_hmac` for lookup uniqueness.
	- Clears legacy plaintext `email` values.
	- Writes batch lifecycle logs (`started`, `completed`, `failed`) and per-user logs (`success`, `error`) to `migration_log`.
	- Sanitizes exception text before persisting to prevent sensitive data leakage.

- `validate_email_migration.py`
	- Verifies migration invariants after a run (no plaintext emails, encrypted/HMAC fields present, no failed logs, completed batch record exists).
	- Returns non-zero exit code when checks fail.

- `monitor_migration_log.py`
	- Monitors `migration_log` for `error`/`failed` records.
	- Supports threshold-based alert behavior via `MIGRATION_ERROR_THRESHOLD`.
	- Returns non-zero exit code when threshold is reached.

## Suggested Run Order (Staging)

1. `python db/migrations/migrate_email_encryption.py`
2. `python db/migrations/validate_email_migration.py`
3. `python db/migrations/monitor_migration_log.py`

Record all outputs in staging validation notes before requesting backend/security lead sign-off.
