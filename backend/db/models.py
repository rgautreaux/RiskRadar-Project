from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, Float, UniqueConstraint, DateTime, JSON
from db.database import Base


def _now():
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Text, nullable=False)            # 'airnow', 'epa', 'nws', 'firms'
    source_id = Column(Text)                          # dedup key from the API
    alert_type = Column(Text, nullable=False)         # 'air_quality', 'weather', 'wildfire', 'pollution'
    severity = Column(Text, nullable=False, default="moderate")
    title = Column(Text, nullable=False)
    description = Column(Text)
    raw_data = Column(JSON)                           # Raw source payload
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(Text)
    event_start = Column(Text)
    event_end = Column(Text)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

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
    generated_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    model_used = Column(Text)
    token_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_token = Column(Text)
    display_name = Column(Text)
    # Deprecated: email (to be removed after migration)
    email = Column(Text, unique=True, nullable=True)
    # New: AES-encrypted email storage
    email_encrypted = Column(Text, unique=True, nullable=True)
    # HMAC of email for uniqueness lookup (not reversible)
    email_hmac = Column(Text, unique=True, nullable=True)
    password_hash = Column(Text)
    zip_code = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    alert_types = Column(Text, default='["all"]')     # JSON array
    notify_severity = Column(Text, default="high")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

# NOTE: Migration required to populate email_encrypted and email_hmac from email.


class ScrapeLog(Base):
    __tablename__ = "scrape_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Text, nullable=False)
    status = Column(Text, nullable=False)             # 'success', 'failure', 'partial'
    alerts_fetched = Column(Integer, default=0)
    alerts_new = Column(Integer, default=0)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False, default=_now)


class AlertArchive(Base):
    __tablename__ = "alerts_archive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_id = Column(Integer, nullable=False, unique=True)
    source = Column(Text, nullable=False)
    source_id = Column(Text)
    alert_type = Column(Text, nullable=False)
    severity = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    raw_data = Column(JSON)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(Text)
    event_start = Column(Text)
    event_end = Column(Text)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    cleanup_run_id = Column(Integer)


class SummaryArchive(Base):
    __tablename__ = "summaries_archive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_id = Column(Integer, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    summary_type = Column(Text, nullable=False)
    alert_ids = Column(Text)
    region = Column(Text)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    model_used = Column(Text)
    token_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    cleanup_run_id = Column(Integer)



class ScrapeLogArchive(Base):
    __tablename__ = "scrape_log_archive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_id = Column(Integer, nullable=False, unique=True)
    source = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    alerts_fetched = Column(Integer, default=0)
    alerts_new = Column(Integer, default=0)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    cleanup_run_id = Column(Integer)


# Migration logging table for email/password migration
class MigrationLog(Base):
    __tablename__ = "migration_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=_now)
    user_id = Column(Integer)
    action = Column(Text)
    status = Column(Text)
    error_message = Column(Text)


class CleanupRun(Base):
    __tablename__ = "cleanup_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(Text, nullable=False)
    schedule_kind = Column(Text, nullable=False)
    cutoff_at = Column(DateTime(timezone=True), nullable=False)
    rows_eligible = Column(Integer, nullable=False, default=0)
    rows_archived = Column(Integer, nullable=False, default=0)
    rows_deleted = Column(Integer, nullable=False, default=0)
    storage_bytes_estimated = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    dry_run = Column(Integer, nullable=False, default=1)
    status = Column(Text, nullable=False, default="success")
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    completed_at = Column(DateTime(timezone=True), nullable=False, default=_now)
