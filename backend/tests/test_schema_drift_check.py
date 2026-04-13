from sqlalchemy import text

from db.migrations import schema_drift_check


def test_schema_drift_check_passes_on_fresh_schema(db_session, monkeypatch):
    monkeypatch.setattr(schema_drift_check, "SessionLocal", lambda: db_session)

    code = schema_drift_check.run_schema_drift_check()

    assert code == 0


def test_schema_drift_check_detects_missing_index(db_session, monkeypatch):
    db_session.execute(text("DROP INDEX idx_alerts_source_fetched_at"))
    db_session.commit()

    monkeypatch.setattr(schema_drift_check, "SessionLocal", lambda: db_session)

    code = schema_drift_check.run_schema_drift_check()

    assert code == 2


def test_schema_drift_check_detects_missing_table(db_session, monkeypatch):
    db_session.execute(text("DROP TABLE notification_dispatch_log"))
    db_session.commit()

    monkeypatch.setattr(schema_drift_check, "SessionLocal", lambda: db_session)

    code = schema_drift_check.run_schema_drift_check()

    assert code == 2
