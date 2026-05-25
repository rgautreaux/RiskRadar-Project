from backend.db.retention import run_retention_cleanup
from backend.config.settings import settings

# Test hook: tests monkeypatch `db.retention.SessionLocal` to inject the
# in-memory test session factory. Provide a module-level name so monkeypatch
# can set it; backend.db.retention.run_retention_cleanup will prefer this
# when present.
SessionLocal = None

__all__ = ["run_retention_cleanup", "SessionLocal", "settings"]
