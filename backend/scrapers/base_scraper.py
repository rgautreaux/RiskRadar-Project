import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from db.database import SessionLocal
from db.models import Alert, ScrapeLog

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    source_name: str = ""
    alert_type: str = ""

    @abstractmethod
    def fetch_raw_data(self) -> list[dict]:
        """Hit the external API, return a list of raw dicts."""
        ...

    @abstractmethod
    def normalize(self, raw: dict) -> dict:
        """Convert a raw API dict into an Alert-compatible dict."""
        ...

    def run(self):
        started = datetime.now(timezone.utc)
        start_ms = time.monotonic_ns() // 1_000_000
        session = SessionLocal()
        log = ScrapeLog(source=self.source_name, started_at=started.isoformat(), status="success")

        try:
            raw_items = self.fetch_raw_data()
            new_count = 0

            for item in raw_items:
                try:
                    normalized = self.normalize(item)
                except Exception as e:
                    logger.warning(f"[{self.source_name}] normalize error: {e}")
                    continue

                # Dedup: skip if (source, source_id) already exists
                existing = (
                    session.query(Alert)
                    .filter_by(source=normalized["source"], source_id=normalized["source_id"])
                    .first()
                )
                if not existing:
                    session.add(Alert(**normalized))
                    new_count += 1

            session.commit()
            log.alerts_fetched = len(raw_items)
            log.alerts_new = new_count
            logger.info(f"[{self.source_name}] fetched={len(raw_items)} new={new_count}")

        except Exception as e:
            log.status = "failure"
            log.error_message = str(e)
            session.rollback()
            logger.error(f"[{self.source_name}] scrape failed: {e}")

        finally:
            elapsed = time.monotonic_ns() // 1_000_000 - start_ms
            log.duration_ms = elapsed
            log.completed_at = datetime.now(timezone.utc).isoformat()
            session.add(log)
            session.commit()
            session.close()
