# Phase 3 Staging Evidence Template

Date:
Environment:
Reviewer Target: Noah + Backend/Security Lead
Operator:
Commit SHA:

## Pre-flight Confirmation

- [ ] Staging environment verified
- [ ] `.env` reviewed for staging-only DB credentials and JWT secret handling
- [ ] Database backup completed and restore path verified
- [ ] Migration scripts verified at intended commit SHA

## Command Evidence

### 1) Apply Schema Migration

Command:

Expected:
- `users.email_encrypted` exists
- `users.email_hmac` exists
- `migration_log` table exists

Actual output:

Exit code:

### 2) Run Email Migration

Command:

Expected:
- Script completes with no batch-level failure
- `migration_log` has `email_encryption_batch` start and final status records

Actual output:

Exit code:

### 3) Run Migration Validator

Command:

Expected:
- Exit code `0`
- `users_plaintext_remaining=0`
- `users_missing_encrypted=0`
- `users_missing_hmac=0`
- `migration_failed_or_error_logs=0`
- `batch_completed_records>=1`

Actual output:

Exit code:

### 4) Run Migration Monitor (Baseline)

Command:

Expected:
- `error_count` below threshold
- `OK: migration error threshold not reached`

Actual output:

Exit code:

### 5) Run Monitor Threshold/Failure Simulation

Command:

Expected:
- Non-zero exit when threshold is reached

Actual output:

Exit code:

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
- [ ] Validator output attached
- [ ] Monitor baseline output attached
- [ ] Monitor threshold test output attached
- [ ] SQL spot-check outputs attached
- [ ] Notes on anomalies (if any) included

## Reviewer Submission Checklist

- [ ] Evidence packet linked in `phase3_review_handoff.md`
- [ ] Noah requested to review secrets handling + data privacy + least-privilege assumptions
- [ ] Backend/Security lead requested to approve gate release or request changes
- [ ] Sign-off section updated with explicit reviewer decisions
