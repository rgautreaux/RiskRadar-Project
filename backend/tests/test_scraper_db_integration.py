"""Integration tests for scraper -> database persistence path.

These tests mock external HTTP APIs but run real scraper classes and BaseScraper.run()
to verify end-to-end writes into Alert and ScrapeLog tables.
"""

from unittest.mock import patch

from db.models import Alert, ScrapeLog
from scrapers.epa_scraper import EPAScraper
from scrapers.generic_api_scraper import GenericAPIScraper
from scrapers.nws_scraper import NWSScraper


class _FakeResponse:
    def __init__(self, payload: dict | list[dict]):
        self._payload = payload
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _build_usgs_config() -> dict:
    return {
        "name": "usgs_earthquakes",
        "enabled": True,
        "alert_type": "earthquake",
        "url": "https://earthquake.usgs.gov/fdsnws/event/1/query",
        "method": "GET",
        "request": {"params": {"format": "geojson"}, "headers": {}},
        "auth": {"type": "none"},
        "response": {"format": "json", "items_path": "features"},
        "field_mapping": {
            "source_id": "id",
            "title": "properties.title",
            "description": "properties.place",
            "latitude": "geometry.coordinates[1]",
            "longitude": "geometry.coordinates[0]",
            "location_name": "properties.place",
            "event_start": "properties.time",
            "event_end": None,
            "raw_data": "__full_item__",
        },
        "severity": {
            "type": "threshold",
            "field": "properties.mag",
            "thresholds": [
                {"gte": 6.0, "value": "critical"},
                {"gte": 4.5, "value": "high"},
                {"gte": 3.0, "value": "moderate"},
                {"default": "low"},
            ],
        },
    }


def _mocked_httpx_get(url, **kwargs):
    if "weather.gov/alerts/active" in url:
        return _FakeResponse(
            {
                "features": [
                    {
                        "properties": {
                            "id": "nws_test_001",
                            "severity": "Severe",
                            "headline": "Test Severe Weather Warning",
                            "description": "Strong winds expected.",
                            "areaDesc": "Los Angeles County",
                            "onset": "2026-03-03T10:00:00Z",
                            "expires": "2026-03-03T14:00:00Z",
                        },
                        "geometry": {"type": "Point", "coordinates": [-118.2437, 34.0522]},
                    }
                ]
            }
        )
    if "data.epa.gov/efservice/tri_facility" in url:
        return _FakeResponse(
            [
                {
                    "tri_facility_id": "EPA001",
                    "facility_name": "Test Facility A",
                    "city_name": "Los Angeles",
                    "state_abbr": "CA",
                    "county_name": "Los Angeles",
                    "pref_latitude": "34.1",
                    "pref_longitude": "-118.3",
                },
                {
                    "tri_facility_id": "EPA002",
                    "facility_name": "Test Facility B",
                    "city_name": "Pasadena",
                    "state_abbr": "CA",
                    "county_name": "Los Angeles",
                    "pref_latitude": "34.2",
                    "pref_longitude": "-118.1",
                },
            ]
        )
    raise AssertionError(f"Unexpected GET URL called: {url}")


def _mocked_usgs_request(method, url, **kwargs):
    if "earthquake.usgs.gov/fdsnws/event/1/query" in url:
        return _FakeResponse(
            {
                "features": [
                    {
                        "id": "usgs_test_001",
                        "properties": {
                            "title": "M 3.4 - Test Quake One",
                            "place": "10km W of Test City",
                            "time": "2026-03-03T09:00:00Z",
                            "mag": 3.4,
                        },
                        "geometry": {"coordinates": [-118.5, 34.3]},
                    },
                    {
                        "id": "usgs_test_002",
                        "properties": {
                            "title": "M 2.8 - Test Quake Two",
                            "place": "5km S of Test City",
                            "time": "2026-03-03T11:00:00Z",
                            "mag": 2.8,
                        },
                        "geometry": {"coordinates": [-118.4, 34.2]},
                    },
                ]
            }
        )
    raise AssertionError(f"Unexpected USGS URL called: {url}")


def test_scrapers_persist_alerts_and_logs_end_to_end(db_session):
    scrapers = [
        NWSScraper(),
        EPAScraper(),
        GenericAPIScraper(_build_usgs_config()),
    ]

    with (
        patch("scrapers.base_scraper.SessionLocal", return_value=db_session),
        patch("httpx.get", side_effect=_mocked_httpx_get),
        patch("scrapers.generic_api_scraper.httpx.request", side_effect=_mocked_usgs_request),
    ):
        for scraper in scrapers:
            scraper.run()

    alerts = db_session.query(Alert).all()
    logs = db_session.query(ScrapeLog).all()

    assert len(alerts) == 5
    assert len(logs) == 3

    nws_alert = db_session.query(Alert).filter(Alert.source == "nws").one()
    assert nws_alert.source_id == "nws_test_001"
    assert nws_alert.severity == "high"

    epa_alerts = db_session.query(Alert).filter(Alert.source == "epa").all()
    assert len(epa_alerts) == 2

    usgs_alerts = db_session.query(Alert).filter(Alert.source == "usgs_earthquakes").all()
    assert len(usgs_alerts) == 2

    nws_log = db_session.query(ScrapeLog).filter(ScrapeLog.source == "nws").one()
    epa_log = db_session.query(ScrapeLog).filter(ScrapeLog.source == "epa").one()
    usgs_log = db_session.query(ScrapeLog).filter(ScrapeLog.source == "usgs_earthquakes").one()

    assert nws_log.status == "success"
    assert nws_log.alerts_fetched == 1
    assert nws_log.alerts_new == 1

    assert epa_log.status == "success"
    assert epa_log.alerts_fetched == 2
    assert epa_log.alerts_new == 2

    assert usgs_log.status == "success"
    assert usgs_log.alerts_fetched == 2
    assert usgs_log.alerts_new == 2


def test_scrapers_second_run_deduplicates_but_logs_again(db_session):
    scrapers = [
        NWSScraper(),
        EPAScraper(),
        GenericAPIScraper(_build_usgs_config()),
    ]

    with (
        patch("scrapers.base_scraper.SessionLocal", return_value=db_session),
        patch("httpx.get", side_effect=_mocked_httpx_get),
        patch("scrapers.generic_api_scraper.httpx.request", side_effect=_mocked_usgs_request),
    ):
        for scraper in scrapers:
            scraper.run()
        for scraper in scrapers:
            scraper.run()

    assert db_session.query(Alert).count() == 5
    assert db_session.query(ScrapeLog).count() == 6

    latest_nws_log = (
        db_session.query(ScrapeLog)
        .filter(ScrapeLog.source == "nws")
        .order_by(ScrapeLog.id.desc())
        .first()
    )
    latest_epa_log = (
        db_session.query(ScrapeLog)
        .filter(ScrapeLog.source == "epa")
        .order_by(ScrapeLog.id.desc())
        .first()
    )
    latest_usgs_log = (
        db_session.query(ScrapeLog)
        .filter(ScrapeLog.source == "usgs_earthquakes")
        .order_by(ScrapeLog.id.desc())
        .first()
    )

    assert latest_nws_log.alerts_fetched == 1
    assert latest_nws_log.alerts_new == 0

    assert latest_epa_log.alerts_fetched == 2
    assert latest_epa_log.alerts_new == 0

    assert latest_usgs_log.alerts_fetched == 2
    assert latest_usgs_log.alerts_new == 0
