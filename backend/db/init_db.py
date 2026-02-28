"""Create all database tables. Safe to run multiple times — only creates missing tables."""

from db.database import engine, Base
from db.models import Alert, Summary, User, ScrapeLog  # noqa: F401 (import so models register)


def init_database():
    Base.metadata.create_all(bind=engine)
    print(f"Database ready: {engine.url}")


if __name__ == "__main__":
    init_database()
