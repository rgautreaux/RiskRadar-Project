# Migration Logging Plan: Email Encryption Migration

## Objective
Ensure all migration actions and errors are logged for traceability and auditing during the email encryption migration.

## Logging Requirements
- Log each batch of migrated users (start/end time, batch size).
- Log individual user migration actions (user ID, email, success/failure).
- Log errors and exceptions with detailed context.
- Store logs in a dedicated table (e.g., migration_log) or file (not versioned).
- Alert on any failed or partial migrations.


## Example Table Definition (SQLAlchemy)
```python
from sqlalchemy import Column, Integer, DateTime, Text
from db.database import Base
import datetime

class MigrationLog(Base):
        __tablename__ = "migration_log"
        id = Column(Integer, primary_key=True, autoincrement=True)
        timestamp = Column(DateTime, default=datetime.datetime.utcnow)
        user_id = Column(Integer)
        action = Column(Text)  # e.g., 'encrypt_email', 'rollback', 'batch_start', 'batch_end'
        status = Column(Text)  # e.g., 'success', 'failure', 'skipped'
        error_message = Column(Text)
```

## Test Database Setup (for Staging/Local)
1. Add the MigrationLog model to your test database (e.g., via Alembic or Base.metadata.create_all()).
2. Use a dedicated test or staging DB, never production.

## Example Log Entries
| timestamp           | user_id | action         | status   | error_message         |
|---------------------|---------|---------------|----------|----------------------|
| 2026-03-23 10:00:00 |   101   | batch_start    | success  | NULL                 |
| 2026-03-23 10:00:01 |   101   | encrypt_email  | success  | NULL                 |
| 2026-03-23 10:00:02 |   102   | encrypt_email  | failure  | 'UnicodeDecodeError' |
| 2026-03-23 10:00:10 |   NULL  | batch_end      | success  | NULL                 |

## Example Monitoring Queries
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

## Logging Setup Documentation
- Ensure all migration scripts write to migration_log at each major step (batch start/end, per-user action, errors).
- Do not log sensitive data (e.g., plaintext emails or keys).
- Validate that logs are written and can be queried in the test/staging environment.
- Review log format and monitoring queries with backend team before production use.

## Example Logging Logic (pseudo-code)
- On batch start: log batch metadata
- For each user:
    - Log migration attempt
    - Log success or error
- On batch end: log completion

## Notes
- Review log format and storage location with backend team.
- Do not store sensitive data in logs.
- Validate logging in staging before production.
