from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from config.settings import settings

database_url = str(settings.DATABASE_URL).strip()
DATABASE_URL = database_url or f"sqlite:///{str(settings.DB_PATH)}"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_write(db: Session):
    """Guarded write block that commits once or rolls back on failure."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
