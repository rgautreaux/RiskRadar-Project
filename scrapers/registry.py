import importlib
from pathlib import Path
import yaml
from types import SimpleNamespace

# Backend module reference
_breg = importlib.import_module("backend.scrapers.registry")

# Expose classes from backend module so tests can monkeypatch them
WebScraper = getattr(_breg, "WebScraper", None)
GenericAPIScraper = getattr(_breg, "GenericAPIScraper", None)
AirNowScraper = getattr(_breg, "AirNowScraper", None)
EPAScraper = getattr(_breg, "EPAScraper", None)
FIRMSScraper = getattr(_breg, "FIRMSScraper", None)
NWSScraper = getattr(_breg, "NWSScraper", None)

# Default settings proxy — copy uppercase attrs to a mutable namespace so
# tests can monkeypatch attributes like `settings.LLM_PROVIDER`.
_backend_settings = getattr(_breg, "settings", None)
_settings_ns = SimpleNamespace()
if _backend_settings is not None:
	for name in dir(_backend_settings):
		if name.isupper():
			try:
				setattr(_settings_ns, name, getattr(_backend_settings, name))
			except Exception:
				pass
# Ensure test-friendly defaults exist for attributes tests patch
for _default_attr in ("LLM_PROVIDER", "LLM_API_KEY", "FIRECRAWL_API_KEY", "LLM_MODEL", "LLM_MAX_TOKENS", "SOURCES_CONFIG_PATH"):
	if not hasattr(_settings_ns, _default_attr):
		setattr(_settings_ns, _default_attr, None)

settings = _settings_ns
# Provide helper methods expected by backend code
setattr(settings, "resolved_llm_provider", lambda: getattr(settings, "LLM_PROVIDER", None))
setattr(settings, "resolved_llm_api_key", lambda: getattr(settings, "LLM_API_KEY", None) or getattr(settings, "OPENROUTER_API_KEY", None))


def _load_yaml_config() -> dict[str, list[dict]]:
	config_path = Path(settings.SOURCES_CONFIG_PATH) if getattr(settings, "SOURCES_CONFIG_PATH", None) else None
	if not config_path or not config_path.exists():
		return {"api_sources": [], "web_sources": []}
	with open(config_path, "r", encoding="utf-8") as fh:
		return yaml.safe_load(fh) or {"api_sources": [], "web_sources": []}


def load_all_scrapers() -> list[dict]:
	"""Call backend.load_all_scrapers while temporarily injecting our
	`settings` and `_load_yaml_config` so tests can monkeypatch those names.
	"""
	bmod = _breg
	orig_settings = getattr(bmod, "settings", None)
	orig_loader = getattr(bmod, "_load_yaml_config", None)
	# Inject
	setattr(bmod, "settings", settings)
	setattr(bmod, "_load_yaml_config", _load_yaml_config)
	try:
		return bmod.load_all_scrapers()
	finally:
		# Restore originals
		if orig_settings is not None:
			setattr(bmod, "settings", orig_settings)
		else:
			try:
				delattr(bmod, "settings")
			except Exception:
				pass
		if orig_loader is not None:
			setattr(bmod, "_load_yaml_config", orig_loader)
		else:
			try:
				delattr(bmod, "_load_yaml_config")
			except Exception:
				pass


__all__ = [
	"load_all_scrapers",
	"_load_yaml_config",
	"WebScraper",
	"GenericAPIScraper",
	"AirNowScraper",
	"EPAScraper",
	"FIRMSScraper",
	"NWSScraper",
	"settings",
]
