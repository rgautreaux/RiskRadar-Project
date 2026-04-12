# Schema Readiness Checklist

Use this checklist before applying any database schema or data migration in staging or production.

## 1) Preconditions

- [ ] Confirm backup completed and restore tested for the target engine.
- [ ] Confirm the active branch contains all required migration scripts.
- [ ] Confirm environment variables for DB connectivity and encryption are set correctly.
- [ ] Confirm no unreviewed local schema changes are pending.

## 2) Required Migration Baseline

Apply in order:

1. `2026-04-10_phase3_email_security_schema.sql`
2. `2026-04-11_notification_channels_dispatch_log.sql`
3. `2026-04-11_operational_index_hardening.sql`
4. `2026-04-12_phase0_index_hardening.sql`
5. `2026-04-12_foreign_key_integrity_hardening.sql`
6. `2026-04-12_mariadb_email_hmac_index_fix.sql` (MariaDB only)

## 3) Preflight Gate

Run:

- `python db/migrations/preflight.py`

Strict mode when validating post-email-migration state:

- `python -c "from db.migrations.preflight import run_preflight; raise SystemExit(run_preflight(strict=True))"`

Blocking conditions include:

- Missing required tables/columns/indexes
- Missing required foreign keys
- Duplicate `users.email_hmac`
- Orphan dispatch references
- Orphan archive cleanup lineage

## 4) Email Migration Safety

Run sequence:

1. `python db/migrations/migrate_email_encryption.py`
2. `python db/migrations/validate_email_migration.py`
3. `python db/migrations/monitor_migration_log.py`

Rollback drill tool:

- `python db/migrations/rollback_email_encryption.py`
- Optional dry run: set `ROLLBACK_DRY_RUN=true`

## 5) Verification

- [ ] Migration scripts executed with no SQL errors.
- [ ] Preflight returns `status=ok`.
- [ ] Email validation returns success (`0`).
- [ ] Monitoring threshold check returns success (`0`).
- [ ] Targeted migration tests pass.
- [ ] Backend regression test suite passes.

## 6) Promotion Go/No-Go

Go only if all are true:

- [ ] No blocking preflight issues.
- [ ] No failed migration or monitor checks.
- [ ] No orphan references.
- [ ] Test suite clean for migration-related changes.
- [ ] Reviewer sign-off recorded.
