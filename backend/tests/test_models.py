"""Tests for database models."""

import hashlib
import json
import pytest
from sqlalchemy.exc import IntegrityError

from db.models import Alert, Summary, User, ScrapeLog
from tests.conftest import NOW


class TestAlertModel:
    def test_create_alert(self, db_session):
        alert = Alert(
            source="test", source_id="t_001", alert_type="weather",
            severity="high", title="Test Alert",
            fetched_at=NOW, created_at=NOW, updated_at=NOW,
        )
        db_session.add(alert)
        db_session.commit()
        assert alert.id is not None
        assert alert.source == "test"

    def test_unique_constraint_source_source_id(self, db_session):
        a1 = Alert(
            source="test", source_id="dup_001", alert_type="weather",
            severity="high", title="Alert 1",
            fetched_at=NOW, created_at=NOW, updated_at=NOW,
        )
        a2 = Alert(
            source="test", source_id="dup_001", alert_type="weather",
            severity="low", title="Alert 2",
            fetched_at=NOW, created_at=NOW, updated_at=NOW,
        )
        db_session.add(a1)
        db_session.commit()
        db_session.add(a2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_optional_fields_nullable(self, db_session):
        alert = Alert(
            source="test", source_id="t_002", alert_type="weather",
            severity="low", title="Minimal Alert",
            fetched_at=NOW, created_at=NOW, updated_at=NOW,
        )
        db_session.add(alert)
        db_session.commit()
        assert alert.description is None
        assert alert.latitude is None
        assert alert.longitude is None


class TestSummaryModel:
    def test_create_summary(self, db_session):
        summary = Summary(
            title="Daily Digest", content="Summary text.",
            summary_type="daily", alert_ids="[1,2]",
            generated_at=NOW, created_at=NOW,
        )
        db_session.add(summary)
        db_session.commit()
        assert summary.id is not None
        assert summary.summary_type == "daily"

    def test_alert_ids_stored_as_json(self, db_session):
        ids = [1, 2, 3]
        summary = Summary(
            title="Test", content="Content",
            summary_type="daily", alert_ids=json.dumps(ids),
            generated_at=NOW, created_at=NOW,
        )
        db_session.add(summary)
        db_session.commit()
        assert json.loads(summary.alert_ids) == ids


class TestUserModel:
    def test_create_user(self, db_session):
        user = User(
            display_name="Alice", email="alice@test.com",
            password_hash=hashlib.sha256(b"pass").hexdigest(),
            created_at=NOW, updated_at=NOW,
        )
        db_session.add(user)
        db_session.commit()
        assert user.id is not None
        assert user.password_hash != "pass"

    def test_unique_email_constraint(self, db_session):
        u1 = User(
            display_name="A", email="same@test.com",
            password_hash="hash1", created_at=NOW, updated_at=NOW,
        )
        u2 = User(
            display_name="B", email="same@test.com",
            password_hash="hash2", created_at=NOW, updated_at=NOW,
        )
        db_session.add(u1)
        db_session.commit()
        db_session.add(u2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestScrapeLogModel:
    def test_create_scrape_log(self, db_session):
        log = ScrapeLog(
            source="nws", status="success",
            alerts_fetched=10, alerts_new=3,
            duration_ms=450,
            started_at=NOW, completed_at=NOW,
        )
        db_session.add(log)
        db_session.commit()
        assert log.id is not None
        assert log.alerts_fetched == 10
        assert log.alerts_new == 3
