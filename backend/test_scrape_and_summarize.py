"""Quick test: scrape data from free APIs and generate a summary.

Run from the backend directory:
    python test_scrape_and_summarize.py
"""

import sys
import logging

from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("test")


def main():
    # --- Step 1: Initialize database ---
    logger.info("=== Step 1: Initializing database ===")
    from db.init_db import init_database
    init_database()
    logger.info("Database initialized.\n")

    # --- Step 2: Run scrapers (no API key needed) ---
    from scrapers.nws_scraper import NWSScraper
    from scrapers.epa_scraper import EPAScraper

    scrapers_to_test = [
        ("NWS (weather)", NWSScraper()),
        ("EPA (pollution)", EPAScraper()),
    ]

    # Also test the USGS config-driven scraper if sources.yaml has it
    try:
        from scrapers.registry import _load_yaml_config
        from scrapers.generic_api_scraper import GenericAPIScraper

        config = _load_yaml_config()
        for api_cfg in config.get("api_sources", []):
            if api_cfg.get("enabled", True) and api_cfg.get("auth", {}).get("type", "none") == "none":
                scrapers_to_test.append(
                    (f"Generic API: {api_cfg['name']}", GenericAPIScraper(api_cfg))
                )
    except Exception as e:
        logger.warning(f"Could not load config-driven scrapers: {e}")

    for name, scraper in scrapers_to_test:
        logger.info(f"=== Step 2: Running {name} scraper ===")
        try:
            scraper.run()
        except Exception as e:
            logger.error(f"{name} scraper failed: {e}")
        print()

    # --- Step 3: Check what we scraped ---
    logger.info("=== Step 3: Checking scraped alerts ===")
    from db.database import SessionLocal
    from db.models import Alert

    db = SessionLocal()
    try:
        alerts = db.query(Alert).all()
        logger.info(f"Total alerts in database: {len(alerts)}")

        if not alerts:
            logger.warning("No alerts were scraped. Cannot generate summary.")
            logger.info("This may be normal if there are no active weather alerts in your area.")
            return

        # Show a few examples
        for a in alerts[:5]:
            print(f"  [{a.source}] {a.severity.upper():10s} | {a.title[:70]}")
        if len(alerts) > 5:
            print(f"  ... and {len(alerts) - 5} more")
        print()

        # --- Step 4: Generate summary ---
        logger.info("=== Step 4: Generating daily digest summary ===")
        from llm.summarizer import Summarizer

        summarizer = Summarizer()
        try:
            summary = summarizer.generate_daily_digest(db, since_hours=24)
            if summary:
                logger.info(f"Summary generated! (model={summary.model_used}, tokens={summary.token_count})")
                print("--- DAILY DIGEST ---")
                print(f"Summary content: {summary.content}")
                print("--- END ---")
            else:
                logger.warning("No summary generated (no recent alerts).")
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            logger.info("This is expected if LLM_API_KEY is not configured.")

    finally:
        db.close()

    logger.info("\nTest complete!")


if __name__ == "__main__":
    main()
