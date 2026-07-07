from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, Float, UniqueConstraint, DateTime, JSON, Boolean, Index, ForeignKey, String
from sqlalchemy.orm import relationship
from db.database import Base


def _now():
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)      # 'airnow', 'epa', 'nws', 'firms'
    source_id = Column(Text)                          # dedup key from the API
    alert_type = Column(String(100), nullable=False)  # 'air_quality', 'weather', 'wildfire', 'pollution'
    severity = Column(String(50), nullable=False, default="moderate")
    title = Column(Text, nullable=False)
    description = Column(Text)
    raw_data = Column(JSON)                           # Legacy raw source payload (deprecated)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))
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
        Index("idx_alerts_source_fetched_at", "source", "fetched_at"),
        Index("idx_alerts_type_severity_fetched_at", "alert_type", "severity", "fetched_at"),
    )

    location = relationship("Location", back_populates="alerts")
    raw_payload_entry = relationship("AlertRawPayload", back_populates="alert", uselist=False)


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)            # LLM-generated markdown
    summary_type = Column(String(50), nullable=False, default="daily")
    alert_ids = Column(Text)                          # Legacy JSON array of alert IDs (deprecated)
    region = Column(Text)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    model_used = Column(Text)
    token_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        Index("idx_summaries_summary_type_generated_at", "summary_type", "generated_at"),
    )

    summary_alerts = relationship("SummaryAlert", back_populates="summary", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_token = Column(Text)
    display_name = Column(Text)
    # Deprecated: email (to be removed after migration)
    email = Column(Text, unique=True, nullable=True)
    # New: AES-encrypted email storage
    email_encrypted = Column(Text, nullable=True)
    # HMAC of email for uniqueness lookup (not reversible)
    email_hmac = Column(String(64), unique=True, nullable=True)
    password_hash = Column(Text)
    zip_code = Column(Text)
    latitude = Column(Float)                           # User override latitude
    longitude = Column(Float)                          # User override longitude
    alert_types = Column(Text, default='["all"]')     # Legacy JSON array (deprecated)
    notify_severity = Column(Text, default="high")
    notify_push = Column(Boolean, nullable=False, default=True)
    notify_email = Column(Boolean, nullable=False, default=False)
    notify_sms = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    alert_type_preferences = relationship(
        "UserAlertTypePreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )

# NOTE: Migration required to populate email_encrypted and email_hmac from email.


class SavedDestination(Base):
    __tablename__ = "saved_destinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city = Column(Text, nullable=False)
    state = Column(Text)
    zip_code = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        UniqueConstraint("user_id", "city", "state", name="uq_user_destination"),
    )


class ScrapeLog(Base):
    __tablename__ = "scrape_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)        # 'success', 'failure', 'partial'
    alerts_fetched = Column(Integer, default=0)
    alerts_new = Column(Integer, default=0)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        Index("idx_scrape_log_source_started_at", "source", "started_at"),
        Index("idx_scrape_log_status_completed_at", "status", "completed_at"),
    )


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
    cleanup_run_id = Column(Integer, ForeignKey("cleanup_runs.id", ondelete="SET NULL"))


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
    cleanup_run_id = Column(Integer, ForeignKey("cleanup_runs.id", ondelete="SET NULL"))


class SummaryAlert(Base):
    __tablename__ = "summary_alerts"

    summary_id = Column(Integer, ForeignKey("summaries.id", ondelete="CASCADE"), primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    summary = relationship("Summary", back_populates="summary_alerts")
    alert = relationship("Alert")

    __table_args__ = (
        Index("idx_summary_alerts_alert_id", "alert_id"),
    )


class UserAlertTypePreference(Base):
    __tablename__ = "user_alert_type_preferences"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    alert_type = Column(String(64), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    user = relationship("User", back_populates="alert_type_preferences")

    __table_args__ = (
        Index("idx_user_alert_type_preferences_alert_type", "alert_type"),
    )


class ZipGeo(Base):
    __tablename__ = "zip_geo"

    zip_code = Column(String(10), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    state = Column(String(8))
    city = Column(String(128))
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    alerts = relationship("Alert", back_populates="location")

    __table_args__ = (
        UniqueConstraint("latitude", "longitude", "location_name", name="uq_locations_lat_lon_name"),
        Index("idx_locations_lat_lon", "latitude", "longitude"),
    )


class AlertRawPayload(Base):
    __tablename__ = "alert_raw_payloads"

    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True)
    raw_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    alert = relationship("Alert", back_populates="raw_payload_entry")


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
    cleanup_run_id = Column(Integer, ForeignKey("cleanup_runs.id", ondelete="SET NULL"))


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
    status = Column(String(50), nullable=False, default="success")
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    completed_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        Index("idx_cleanup_runs_status_started_at", "status", "started_at"),
    )


class MigrationLog(Base):
    __tablename__ = "migration_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=_now)
    user_id = Column(Integer, nullable=True)
    action = Column(Text, nullable=True)
    status = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)


class NotificationDispatchLog(Base):
    __tablename__ = "notification_dispatch_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="RESTRICT"), nullable=False)
    initiated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    provider = Column(Text, nullable=False)
    recipients_total = Column(Integer, nullable=False, default=0)
    sent_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="success")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)

    __table_args__ = (
        Index("idx_notification_dispatch_status_created_at", "status", "created_at"),
        Index("idx_notification_dispatch_initiated_by_user_id", "initiated_by_user_id"),
    )
