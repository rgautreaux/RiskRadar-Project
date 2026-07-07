"""Source registry — loads sources.yaml, instantiates scraper objects."""

import logging
import os
from pathlib import Path

import yaml

from config.settings import settings
from scrapers.base_scraper import BaseScraper
from scrapers.generic_api_scraper import GenericAPIScraper
from scrapers.web_scraper import WebScraper
from scrapers.nws_scraper import NWSScraper
from scrapers.airnow_scraper import AirNowScraper
from scrapers.epa_scraper import EPAScraper
from scrapers.firms_scraper import FIRMSScraper

logger = logging.getLogger(__name__)

# Legacy scrapers with custom Python logic.
# These coexist alongside config-driven sources from sources.yaml.
LEGACY_SCRAPERS: list[dict] = [
    {
        "factory": lambda: NWSScraper(),
        "id": "nws",
        "interval_minutes": None,
        "requires_env": None,
        "stagger_offset_minutes": 0,
    },
    {
        "factory": lambda: AirNowScraper(),
        "id": "airnow",
        "interval_minutes": None,
        "requires_env": None,
        "stagger_offset_minutes": 1,
    },
    {
        "factory": lambda: EPAScraper(),
        "id": "epa",
        "interval_minutes": 60,
        "requires_env": None,
        "stagger_offset_minutes": 3,
    },
    {
        "factory": lambda: FIRMSScraper(),
        "id": "firms",
        "interval_minutes": None,
        "requires_env": "NASA_FIRMS_MAP_KEY",
        "stagger_offset_minutes": 5,
    },
]


def _load_yaml_config() -> dict:
    """Load and parse the sources.yaml config file."""
    config_path = Path(settings.SOURCES_CONFIG_PATH)
    if not config_path.exists():
        logger.warning(f"Sources config not found at {config_path}, using empty config")
        return {"api_sources": [], "web_sources": []}

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}

    return config


def load_all_scrapers() -> list[dict]:
    """Return a list of scraper descriptors for the scheduler.

    Each descriptor is a dict with:
      - "scraper": BaseScraper instance
      - "id": unique string ID for APScheduler
      - "interval_minutes": int or None (None => use global default)
      - "stagger_offset_minutes": int (to avoid thundering herd)
    """
    scrapers = []

    # 1) Legacy scrapers (the original four)
    for entry in LEGACY_SCRAPERS:
        if entry["requires_env"]:
            if not os.environ.get(entry["requires_env"], ""):
                logger.info(
                    f"Skipping legacy scraper '{entry['id']}': "
                    f"{entry['requires_env']} not set"
                )
                continue
        scrapers.append({
            "scraper": entry["factory"](),
            "id": entry["id"],
            "interval_minutes": entry["interval_minutes"],
            "stagger_offset_minutes": entry["stagger_offset_minutes"],
        })

    # 2) Config-driven API scrapers
    config = _load_yaml_config()
    stagger = 7  # start after legacy scrapers

    for api_cfg in config.get("api_sources", []):
        if not api_cfg.get("enabled", True):
            continue
        auth = api_cfg.get("auth", {})
        if auth.get("type", "none") != "none" and auth.get("env_var"):
            if not os.environ.get(auth["env_var"], ""):
                logger.info(
                    f"Skipping API source '{api_cfg['name']}': "
                    f"{auth['env_var']} not set"
                )
                continue

        scrapers.append({
            "scraper": GenericAPIScraper(api_cfg),
            "id": f"api_{api_cfg['name']}",
            "interval_minutes": api_cfg.get("interval_minutes"),
            "stagger_offset_minutes": stagger,
        })
        stagger += 1

    # 3) Config-driven web scrapers
    for web_cfg in config.get("web_sources", []):
        if not web_cfg.get("enabled", True):
            continue
        llm_provider = settings.resolved_llm_provider()
        llm_api_key = settings.resolved_llm_api_key()

        if not settings.FIRECRAWL_API_KEY:
            logger.info(
                f"Skipping web source '{web_cfg['name']}': FIRECRAWL_API_KEY not set"
            )
            continue
        if llm_provider not in {"openrouter", "openai", "deepseek", "anthropic"}:
            logger.info(
                "Skipping web source '%s': unsupported LLM_PROVIDER '%s'",
                web_cfg['name'],
                llm_provider,
            )
            continue
        if not llm_api_key:
            logger.info(
                "Skipping web source '%s': LLM_API_KEY or OPENROUTER_API_KEY not set",
                web_cfg['name']
            )
            continue

        scrapers.append({
            "scraper": WebScraper(web_cfg),
            "id": f"web_{web_cfg['name']}",
            "interval_minutes": web_cfg.get("interval_minutes"),
            "stagger_offset_minutes": stagger,
        })
        stagger += 2  # web scrapers are slower, give more stagger space

    logger.info(f"Registry loaded: {len(scrapers)} scrapers total")
    return scrapers
