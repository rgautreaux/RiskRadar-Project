# Phase 3 Staging Evidence Template

Date: April 12, 2026
Environment: Local SQLite snapshot
Reviewer Target: Noah + Backend/Security Lead
Operator: Rebecca
Commit SHA: 43a0c401

## Pre-flight Confirmation

- [x] Staging environment verified
- [x] `.env` reviewed for staging-only DB credentials and JWT secret handling
- [ ] Database backup completed and restore path verified
- [x] Migration scripts verified at intended commit SHA

## Command Evidence

### 1) Apply Schema Migration

Command:

- Not executed in this local coordination verification run.

Expected:
- `users.email_encrypted` exists
- `users.email_hmac` exists
- `migration_log` table exists

Actual output:

- N/A for this run.

Exit code:

- N/A

### 2) Run Email Migration

Command:

- Not executed in this local coordination verification run.

Expected:
- Script completes with no batch-level failure
- `migration_log` has `email_encryption_batch` start and final status records

Actual output:

- N/A for this run.

Exit code:

- N/A

### 3) Run Migration Validator

Command:

- `python backend/db/migrations/validate_email_migration.py`

Expected:
- Exit code `0`
- `users_plaintext_remaining=0`
- `users_missing_encrypted=0`
- `users_missing_hmac=0`
- `migration_failed_or_error_logs=0`
- `batch_completed_records>=1`

Actual output:

- `[2026-04-12T18:23:14.670346+00:00] Email migration validation report`
- `users_total=0`
- `users_plaintext_remaining=0`
- `users_missing_encrypted=0`
- `users_missing_hmac=0`
- `migration_failed_or_error_logs=1`
- `batch_completed_records=1`

Exit code:

- `1`

### 4) Run Migration Monitor (Baseline)

Command:

- `python backend/db/migrations/monitor_migration_log.py`

Expected:
- `error_count` below threshold
- `OK: migration error threshold not reached`

Actual output:

- `[2026-04-12T18:23:15.226018+00:00] Migration monitor report`
- `latest_batch_started_at=2026-04-11 17:10:02.759532`
- `error_count=0`
- `threshold=1`
- `OK: migration error threshold not reached`

Exit code:

- `0`

### 5) Run Monitor Threshold/Failure Simulation

Command:

- Not executed in this local coordination verification run.

Expected:
- Non-zero exit when threshold is reached

Actual output:

- N/A for this run.

Exit code:

- N/A

## SQL Spot-Checks (Attach Output)

### Schema checks

```sql
SHOW COLUMNS FROM users LIKE 'email_encrypted';
SHOW COLUMNS FROM users LIKE 'email_hmac';
SHOW TABLES LIKE 'migration_log';
```

### Batch lifecycle checks

```sql
SELECT action, status, timestamp, user_id, error_message
FROM migration_log
WHERE action IN ('email_encryption_batch', 'email_encryption')
ORDER BY timestamp DESC
LIMIT 50;
```

### Summary counts

```sql
SELECT action, status, COUNT(*) AS count
FROM migration_log
GROUP BY action, status
ORDER BY action, status;
```

### Privacy check (no plaintext email leakage in migration logs)

```sql
SELECT id, timestamp, action, status, error_message
FROM migration_log
WHERE error_message LIKE '%@%'
ORDER BY timestamp DESC
LIMIT 20;
```

## Evidence Bundle Checklist

- [ ] Schema migration output attached
- [ ] Migration output attached
- [x] Validator output attached
- [x] Monitor baseline output attached
- [ ] Monitor threshold test output attached
- [ ] SQL spot-check outputs attached
- [x] Notes on anomalies (if any) included

## Reviewer Submission Checklist

- [ ] Evidence packet linked in `phase3_review_handoff.md`
- [ ] Noah requested to review secrets handling + data privacy + least-privilege assumptions
- [ ] Backend/Security lead requested to approve gate release or request changes
- [ ] Sign-off section updated with explicit reviewer decisions
