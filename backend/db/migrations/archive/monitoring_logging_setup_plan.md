# Monitoring & Logging Tool Setup Plan: Email Encryption Migration

## Objective
Prepare monitoring and logging tools to track migration progress, detect anomalies, and support post-deployment auditing.

## Monitoring Requirements
- Monitor migration log table for errors, failed migrations, and batch statistics.
- Set up alerts for high error rates or partial migrations.
- Track database health and user activity post-migration.
- Review logs regularly for suspicious activity or regressions.

## Tool Options
- Use SQL queries to monitor migration_log table.
- Integrate with existing logging/monitoring tools (e.g., ELK stack, Grafana, custom dashboards).
- Set up automated email or Slack alerts for migration failures.

## Implemented Monitoring Path (Apr 2, 2026)
- Script: `db/migrations/monitor_migration_log.py`
- Behavior:
  - Reads `migration_log` and counts `error`/`failed` events.
  - Prints recent error entries for triage.
  - Triggers alert-style non-zero exit when threshold is reached.
- Config:
  - `MIGRATION_ERROR_THRESHOLD` (default: `1`)

## Example SQL Monitoring Queries
- Count failed migrations:
  ```sql
  SELECT COUNT(*) FROM migration_log WHERE status = 'failure';
  ```
- List recent errors:
  ```sql
  SELECT * FROM migration_log WHERE status = 'failure' ORDER BY timestamp DESC LIMIT 10;
  ```
- Monitor batch statistics:
  ```sql
  SELECT action, COUNT(*) FROM migration_log GROUP BY action;
  ```

## Notes
- Validate monitoring setup in staging before production.
- Document monitoring procedures for maintainers.
- Coordinate alerting thresholds and notification channels with backend team.

## Staging Run Commands

1. Run migration:
  - `python db/migrations/migrate_email_encryption.py`
2. Validate migration integrity:
  - `python db/migrations/validate_email_migration.py`
3. Run migration monitoring check:
  - `python db/migrations/monitor_migration_log.py`

Recommended: attach command output to the Phase 3 review handoff doc for backend/security lead approval.
