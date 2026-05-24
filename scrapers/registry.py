import importlib

# Import the backend implementation and re-expose the names tests expect
_breg = importlib.import_module("backend.scrapers.registry")

load_all_scrapers = _breg.load_all_scrapers
_load_yaml_config = _breg._load_yaml_config

# Expose classes and settings for monkeypatching in tests
WebScraper = getattr(_breg, "WebScraper", None)
GenericAPIScraper = getattr(_breg, "GenericAPIScraper", None)
AirNowScraper = getattr(_breg, "AirNowScraper", None)
EPAScraper = getattr(_breg, "EPAScraper", None)
FIRMSScraper = getattr(_breg, "FIRMSScraper", None)
NWSScraper = getattr(_breg, "NWSScraper", None)

# Forward settings so tests can patch `scrapers.registry.settings`
settings = getattr(_breg, "settings", None)

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
