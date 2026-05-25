from backend.db.retention import *

# Test hook: tests monkeypatch `db.retention.SessionLocal` to inject the
# in-memory test session factory. Provide a module-level name so monkeypatch
# can set it; backend.db.retention.run_retention_cleanup will prefer this
# when present.
SessionLocal = None
from importlib import import_module

# Expose a `settings` object that tests can monkeypatch; default to the
# backend config settings instance so runtime behaves the same.
try:
	settings = import_module("backend.config.settings").settings
except Exception:
	settings = None
