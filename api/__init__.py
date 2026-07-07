"""Top-level API package shim. Submodules re-export backend.api.* modules.

Avoid importing backend.api.router here to prevent circular imports during tests.
"""
