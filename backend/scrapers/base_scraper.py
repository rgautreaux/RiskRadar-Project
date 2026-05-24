import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError

from db.database import SessionLocal
from db.models import Alert, ScrapeLog

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    source_name: str = ""
    alert_type: str = ""

    @abstractmethod
    def fetch_raw_data(self) -> list[dict]:
        """Hit the external API, return a list of raw dicts."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: dict) -> dict:
        """Convert a raw API dict into an Alert-compatible dict."""
        raise NotImplementedError

    def run(self):
        started = datetime.now(timezone.utc)
        start_ms = time.monotonic_ns() // 1_000_000
        session = SessionLocal()
        log = ScrapeLog(source=self.source_name, started_at=started, status="success")
        new_count = 0

        try:
            raw_items = self.fetch_raw_data()

            for item in raw_items:
                try:
                    normalized = self.normalize(item)
                except (ValueError, KeyError, TypeError) as exc:
                    logger.warning("[%s] normalize error: %s", self.source_name, exc)
                    continue

                # Dedup: skip if (source, source_id) already exists.
                # no_autoflush prevents pending Alert objects added earlier
                # in this loop from being flushed to the DB mid-iteration,
                # which would trigger a premature INSERT before commit.
                with session.no_autoflush:
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

        except SQLAlchemyError as exc:
            log.status = "failure"
            log.error_message = str(exc)
            session.rollback()
            logger.error("[%s] scrape failed: %s", self.source_name, exc)

        finally:
            elapsed = time.monotonic_ns() // 1_000_000 - start_ms
            log.duration_ms = elapsed
            log.completed_at = datetime.now(timezone.utc)
            session.add(log)
            session.commit()
            session.close()

        return new_count
