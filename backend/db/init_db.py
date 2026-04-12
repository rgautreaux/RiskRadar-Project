"""Create all database tables. Safe to run multiple times — only creates missing tables."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from db.database import engine, Base
from db.models import (
    Alert,
    AlertArchive,
    CleanupRun,
    MigrationLog,
    NotificationDispatchLog,
    ScrapeLog,
    ScrapeLogArchive,
    Summary,
    SummaryArchive,
    User,
)

REGISTERED_MODELS = (
    Alert,
    AlertArchive,
    CleanupRun,
    MigrationLog,
    NotificationDispatchLog,
    ScrapeLog,
    ScrapeLogArchive,
    Summary,
    SummaryArchive,
    User,
)


def init_database():
    _ = REGISTERED_MODELS
    Base.metadata.create_all(bind=engine)
    print(f"Database ready: {engine.url}")


if __name__ == "__main__":
    init_database()
