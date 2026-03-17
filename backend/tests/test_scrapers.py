"""Tests for scraper logic."""

import json
import pytest
from unittest.mock import patch, MagicMock

from scrapers.airnow_scraper import _aqi_to_severity
from scrapers.firms_scraper import _fire_severity
from scrapers.generic_api_scraper import (
    _extract_path, _resolve_template, _safe_float, _build_template_vars,
    GenericAPIScraper,
)
from scrapers.web_scraper import WebScraper


# ---------------------------------------------------------------------------
# AirNow severity mapping
# ---------------------------------------------------------------------------

class TestAqiToSeverity:
    def test_good(self):
        assert _aqi_to_severity(30) == "low"
        assert _aqi_to_severity(50) == "low"

    def test_moderate(self):
        assert _aqi_to_severity(51) == "moderate"
        assert _aqi_to_severity(100) == "moderate"

    def test_high(self):
        assert _aqi_to_severity(101) == "high"
        assert _aqi_to_severity(200) == "high"

    def test_critical(self):
        assert _aqi_to_severity(201) == "critical"
        assert _aqi_to_severity(500) == "critical"


# ---------------------------------------------------------------------------
# FIRMS fire severity
# ---------------------------------------------------------------------------

class TestFireSeverity:
    def test_high_confidence_high_brightness(self):
        assert _fire_severity("high", 450) == "critical"

    def test_high_confidence_low_brightness(self):
        assert _fire_severity("high", 350) == "high"

    def test_nominal_confidence(self):
        assert _fire_severity("nominal", 300) == "moderate"

    def test_low_confidence(self):
        assert _fire_severity("low", 300) == "low"


# ---------------------------------------------------------------------------
# GenericAPIScraper helpers
# ---------------------------------------------------------------------------

class TestExtractPath:
    def test_simple_key(self):
        assert _extract_path({"a": 1}, "a") == 1

    def test_nested_dot(self):
        assert _extract_path({"a": {"b": {"c": 42}}}, "a.b.c") == 42

    def test_array_index(self):
        assert _extract_path({"coords": [10, 20, 30]}, "coords[1]") == 20

    def test_nested_with_array(self):
        data = {"geometry": {"coordinates": [-118.24, 34.05]}}
        assert _extract_path(data, "geometry.coordinates[0]") == -118.24
        assert _extract_path(data, "geometry.coordinates[1]") == 34.05

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            _extract_path({"a": 1}, "b")

    def test_empty_path(self):
        obj = {"a": 1}
        assert _extract_path(obj, "") == obj


class TestResolveTemplate:
    def test_replaces_placeholder(self):
        result = _resolve_template("{default_lat}", {"default_lat": "34.05"})
        assert result == "34.05"

    def test_multiple_placeholders(self):
        result = _resolve_template("{lat},{lon}", {"lat": "34", "lon": "-118"})
        assert result == "34,-118"

    def test_no_placeholder(self):
        assert _resolve_template("hello", {"key": "val"}) == "hello"

    def test_non_string_passthrough(self):
        assert _resolve_template(42, {"key": "val"}) == 42


class TestSafeFloat:
    def test_valid_float(self):
        assert _safe_float("34.05") == 34.05

    def test_valid_int(self):
        assert _safe_float(10) == 10.0

    def test_none(self):
        assert _safe_float(None) is None

    def test_invalid_string(self):
        assert _safe_float("not_a_number") is None


class TestBuildTemplateVars:
    def test_has_expected_keys(self):
        tpl = _build_template_vars()
        assert "today" in tpl
        assert "today_minus_1" in tpl
        assert "today_minus_7" in tpl
        assert "default_lat" in tpl
        assert "default_lon" in tpl
        assert "default_zip" in tpl


# ---------------------------------------------------------------------------
# GenericAPIScraper severity computation
# ---------------------------------------------------------------------------

class TestGenericSeverity:
    def _make_scraper(self, severity_config):
        config = {
            "name": "test",
            "alert_type": "test",
            "severity": severity_config,
            "field_mapping": {},
        }
        return GenericAPIScraper(config)

    def test_fixed_severity(self):
        scraper = self._make_scraper({"type": "fixed", "value": "critical"})
        assert scraper._compute_severity({}) == "critical"

    def test_mapping_severity(self):
        scraper = self._make_scraper({
            "type": "mapping",
            "field": "urgency",
            "map": {"Immediate": "critical", "Expected": "high"},
            "default": "low",
        })
        assert scraper._compute_severity({"urgency": "Immediate"}) == "critical"
        assert scraper._compute_severity({"urgency": "Expected"}) == "high"
        assert scraper._compute_severity({"urgency": "Unknown"}) == "low"

    def test_threshold_severity(self):
        scraper = self._make_scraper({
            "type": "threshold",
            "field": "magnitude",
            "thresholds": [
                {"gte": 6.0, "value": "critical"},
                {"gte": 4.0, "value": "high"},
                {"default": "low"},
            ],
        })
        assert scraper._compute_severity({"magnitude": 7.0}) == "critical"
        assert scraper._compute_severity({"magnitude": 5.0}) == "high"
        assert scraper._compute_severity({"magnitude": 2.0}) == "low"

    def test_missing_field_returns_default(self):
        scraper = self._make_scraper({
            "type": "mapping",
            "field": "missing_field",
            "map": {},
            "default": "moderate",
        })
        assert scraper._compute_severity({}) == "moderate"


# ---------------------------------------------------------------------------
# GenericAPIScraper normalize
# ---------------------------------------------------------------------------

class TestGenericNormalize:
    def test_normalize_maps_fields(self):
        config = {
            "name": "usgs",
            "alert_type": "earthquake",
            "field_mapping": {
                "source_id": "id",
                "title": "properties.title",
                "description": "properties.place",
                "latitude": "geometry.coordinates[1]",
                "longitude": "geometry.coordinates[0]",
                "location_name": "properties.place",
                "event_start": "properties.time",
                "event_end": None,
            },
            "severity": {"type": "fixed", "value": "moderate"},
        }
        scraper = GenericAPIScraper(config)
        raw = {
            "id": "us7000abc",
            "properties": {
                "title": "M 3.5 - Los Angeles",
                "place": "10km W of LA",
                "time": "2026-03-02T12:00:00",
            },
            "geometry": {"coordinates": [-118.24, 34.05]},
        }
        result = scraper.normalize(raw)
        assert result["source"] == "usgs"
        assert result["source_id"] == "us7000abc"
        assert result["title"] == "M 3.5 - Los Angeles"
        assert result["latitude"] == 34.05
        assert result["longitude"] == -118.24
        assert result["severity"] == "moderate"


# ---------------------------------------------------------------------------
# WebScraper normalize
# ---------------------------------------------------------------------------

class TestWebScraperNormalize:
    def test_normalize_passthrough(self):
        config = {"name": "test_web", "alert_type": "wildfire"}
        scraper = WebScraper(config)
        raw = {
            "source_id": "fire_001",
            "title": "Active Fire in County",
            "description": "Large fire detected.",
            "severity": "high",
            "latitude": 34.1,
            "longitude": -118.3,
            "location_name": "Test County",
            "event_start": "2026-03-02",
            "event_end": None,
        }
        result = scraper.normalize(raw)
        assert result["source"] == "test_web"
        assert result["title"] == "Active Fire in County"
        assert result["severity"] == "high"
        assert result["latitude"] == 34.1

    def test_normalize_defaults_missing_fields(self):
        config = {"name": "test_web", "alert_type": "wildfire"}
        scraper = WebScraper(config)
        result = scraper.normalize({})
        assert result["source"] == "test_web"
        assert result["severity"] == "moderate"
        assert result["title"] == "test_web alert"


# ---------------------------------------------------------------------------
# BaseScraper.run() integration
# ---------------------------------------------------------------------------

class TestBaseScraperRun:
    def test_run_deduplicates(self, db_session):
        """Running the same scraper twice should not create duplicate alerts."""
        from scrapers.base_scraper import BaseScraper

        class FakeScraper(BaseScraper):
            source_name = "fake"
            alert_type = "test"

            def fetch_raw_data(self):
                return [{"id": "1"}, {"id": "2"}]

            def normalize(self, raw):
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                return {
                    "source": self.source_name,
                    "source_id": f"fake_{raw['id']}",
                    "alert_type": self.alert_type,
                    "severity": "low",
                    "title": f"Fake alert {raw['id']}",
                    "description": "",
                    "raw_data": {},
                    "latitude": None,
                    "longitude": None,
                    "location_name": "",
                    "event_start": None,
                    "event_end": None,
                    "fetched_at": now,
                    "created_at": now,
                    "updated_at": now,
                }

        with patch("scrapers.base_scraper.SessionLocal", return_value=db_session):
            scraper = FakeScraper()
            scraper.run()  # first run: 2 new
            scraper.run()  # second run: 0 new (dedup)

        from db.models import Alert
        alerts = db_session.query(Alert).filter(Alert.source == "fake").all()
        assert len(alerts) == 2

    def test_run_creates_scrape_log(self, db_session):
        """Each run should create a ScrapeLog entry."""
        from scrapers.base_scraper import BaseScraper
        from db.models import ScrapeLog

        class EmptyScraper(BaseScraper):
            source_name = "empty"
            alert_type = "test"

            def fetch_raw_data(self):
                return []

            def normalize(self, raw):
                return {}

        with patch("scrapers.base_scraper.SessionLocal", return_value=db_session):
            EmptyScraper().run()

        logs = db_session.query(ScrapeLog).filter(ScrapeLog.source == "empty").all()
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].alerts_fetched == 0
