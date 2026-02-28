from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, Float, UniqueConstraint
from db.database import Base


def _now():
    return datetime.now(timezone.utc).isoformat()


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Text, nullable=False)            # 'airnow', 'epa', 'nws', 'firms'
    source_id = Column(Text)                          # dedup key from the API
    alert_type = Column(Text, nullable=False)         # 'air_quality', 'weather', 'wildfire', 'pollution'
    severity = Column(Text, nullable=False, default="moderate")
    title = Column(Text, nullable=False)
    description = Column(Text)
    raw_data = Column(Text)                           # JSON string
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(Text)
    event_start = Column(Text)
    event_end = Column(Text)
    fetched_at = Column(Text, nullable=False, default=_now)
    created_at = Column(Text, nullable=False, default=_now)
    updated_at = Column(Text, nullable=False, default=_now, onupdate=_now)

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_source_alert"),
    )


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)            # LLM-generated markdown
    summary_type = Column(Text, nullable=False, default="daily")
    alert_ids = Column(Text)                          # JSON array of alert IDs
    region = Column(Text)
    generated_at = Column(Text, nullable=False, default=_now)
    model_used = Column(Text)
    token_count = Column(Integer)
    created_at = Column(Text, nullable=False, default=_now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_token = Column(Text)
    display_name = Column(Text)
    email = Column(Text, unique=True)
    password_hash = Column(Text)
    zip_code = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    alert_types = Column(Text, default='["all"]')     # JSON array
    notify_severity = Column(Text, default="high")
    created_at = Column(Text, nullable=False, default=_now)
    updated_at = Column(Text, nullable=False, default=_now, onupdate=_now)


class ScrapeLog(Base):
    __tablename__ = "scrape_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Text, nullable=False)
    status = Column(Text, nullable=False)             # 'success', 'failure', 'partial'
    alerts_fetched = Column(Integer, default=0)
    alerts_new = Column(Integer, default=0)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    started_at = Column(Text, nullable=False)
    completed_at = Column(Text, nullable=False, default=_now)
