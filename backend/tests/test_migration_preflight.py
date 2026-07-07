from datetime import datetime, timezone
from importlib import import_module
from sqlalchemy import text

migration_preflight = import_module("db.migrations.preflight")
models_module = import_module("db.models")
NotificationDispatchLog = models_module.NotificationDispatchLog
User = models_module.User

NOW = datetime.now(timezone.utc)


def test_preflight_passes_on_clean_database(db_session, monkeypatch):
    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 0


def test_preflight_strict_blocks_plaintext_email_rows(db_session, monkeypatch):
    user = User(
        display_name="Legacy User",
        email="legacy@example.com",
        password_hash="hash",
        created_at=NOW,
        updated_at=NOW,
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight(strict=True)

    assert code == 2


def test_preflight_blocks_orphan_notification_dispatch_rows(db_session, monkeypatch):
    dispatch_log = NotificationDispatchLog(
        alert_id=999,
        initiated_by_user_id=999,
        provider="noop",
        recipients_total=0,
        sent_count=0,
        failed_count=0,
        status="success",
        created_at=NOW,
    )
    db_session.add(dispatch_log)
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2


def test_preflight_blocks_missing_required_index(db_session, monkeypatch):
    db_session.execute(text("DROP INDEX idx_alerts_source_fetched_at"))
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2


def test_preflight_blocks_missing_required_foreign_keys(db_session, monkeypatch):
    db_session.execute(text("PRAGMA foreign_keys=OFF"))
    db_session.execute(text("""
        CREATE TABLE notification_dispatch_log_tmp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            initiated_by_user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            recipients_total INTEGER NOT NULL DEFAULT 0,
            sent_count INTEGER NOT NULL DEFAULT 0,
            failed_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            error_message TEXT,
            created_at DATETIME NOT NULL
        )
    """))
    db_session.execute(text("INSERT INTO notification_dispatch_log_tmp SELECT * FROM notification_dispatch_log"))
    db_session.execute(text("DROP TABLE notification_dispatch_log"))
    db_session.execute(text("ALTER TABLE notification_dispatch_log_tmp RENAME TO notification_dispatch_log"))
    db_session.execute(text("CREATE INDEX idx_notification_dispatch_status_created_at ON notification_dispatch_log (status, created_at)"))
    db_session.execute(text("CREATE INDEX idx_notification_dispatch_initiated_by_user_id ON notification_dispatch_log (initiated_by_user_id)"))
    db_session.execute(text("PRAGMA foreign_keys=ON"))
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2


def test_preflight_blocks_legacy_user_prefernces_table(db_session, monkeypatch):
    db_session.execute(
        text(
            """
            CREATE TABLE user_prefernces (
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                is_enabled INTEGER NOT NULL,
                PRIMARY KEY (user_id, category_id)
            )
            """
        )
    )
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2


def test_preflight_blocks_legacy_user_reads_articlle_id_column(db_session, monkeypatch):
    db_session.execute(
        text(
            """
            CREATE TABLE user_reads (
                user_id INTEGER NOT NULL,
                articlle_id INTEGER NOT NULL,
                read_at DATETIME,
                progress_pct INTEGER,
                PRIMARY KEY (user_id, articlle_id)
            )
            """
        )
    )
    db_session.commit()

    monkeypatch.setattr(migration_preflight, "SessionLocal", lambda: db_session)

    code = migration_preflight.run_preflight()

    assert code == 2
