"""Top-level db.migrations package that forwards to backend.db.migrations.

This sets the package __path__ to the backend migrations path so submodules
like `db.migrations.backfill_summary_alerts` can be imported, and re-exports
public names from the backend package.
"""
import importlib

# Load backend migrations package
_backend = importlib.import_module("backend.db.migrations")

# Use backend package path so submodule imports resolve to the backend sources
__path__ = list(getattr(_backend, "__path__", []))

# Re-export public names from backend.db.migrations
from backend.db.migrations import *  # noqa: F401,F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]
