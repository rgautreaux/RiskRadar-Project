"""Tests for the source registry."""

from unittest.mock import patch
import yaml

from scrapers.registry import load_all_scrapers, _load_yaml_config


class TestLoadYamlConfig:
    def test_missing_file_returns_empty(self, tmp_path):
        with patch("scrapers.registry.settings") as mock_settings:
            mock_settings.SOURCES_CONFIG_PATH = str(tmp_path / "nonexistent.yaml")
            config = _load_yaml_config()
        assert config == {"api_sources": [], "web_sources": []}

    def test_valid_yaml(self, tmp_path):
        yaml_content = {
            "api_sources": [{"name": "test_api", "enabled": True}],
            "web_sources": [],
        }
        yaml_file = tmp_path / "sources.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        with patch("scrapers.registry.settings") as mock_settings:
            mock_settings.SOURCES_CONFIG_PATH = str(yaml_file)
            config = _load_yaml_config()
        assert len(config["api_sources"]) == 1
        assert config["api_sources"][0]["name"] == "test_api"


class TestLoadAllScrapers:
    def test_loads_legacy_scrapers(self):
        """With empty YAML config, should still load legacy scrapers."""
        empty_config = {"api_sources": [], "web_sources": []}
        with patch("scrapers.registry._load_yaml_config", return_value=empty_config):
            scrapers = load_all_scrapers()

        ids = [s["id"] for s in scrapers]
        assert "nws" in ids
        assert "epa" in ids

    def test_skips_disabled_api_source(self):
        config = {
            "api_sources": [{
                "name": "disabled_source",
                "enabled": False,
                "alert_type": "test",
                "url": "http://example.com",
                "auth": {"type": "none"},
            }],
            "web_sources": [],
        }
        with patch("scrapers.registry._load_yaml_config", return_value=config):
            scrapers = load_all_scrapers()

        ids = [s["id"] for s in scrapers]
        assert "api_disabled_source" not in ids

    def test_loads_enabled_api_source(self):
        config = {
            "api_sources": [{
                "name": "test_source",
                "enabled": True,
                "alert_type": "test",
                "url": "http://example.com",
                "auth": {"type": "none"},
                "field_mapping": {"source_id": "id", "title": "name"},
                "severity": {"type": "fixed", "value": "low"},
                "response": {"format": "json"},
            }],
            "web_sources": [],
        }
        with patch("scrapers.registry._load_yaml_config", return_value=config):
            scrapers = load_all_scrapers()

        ids = [s["id"] for s in scrapers]
        assert "api_test_source" in ids

    def test_scraper_descriptor_structure(self):
        empty_config = {"api_sources": [], "web_sources": []}
        with patch("scrapers.registry._load_yaml_config", return_value=empty_config):
            scrapers = load_all_scrapers()

        for s in scrapers:
            assert "scraper" in s
            assert "id" in s
            assert "interval_minutes" in s
            assert "stagger_offset_minutes" in s

    def test_skips_web_source_without_firecrawl_key(self):
        config = {
            "api_sources": [],
            "web_sources": [{
                "name": "test_web",
                "enabled": True,
                "alert_type": "test",
                "url": "http://example.com",
            }],
        }
        with patch("scrapers.registry._load_yaml_config", return_value=config), \
             patch("scrapers.registry.settings") as mock_settings:
            mock_settings.FIRECRAWL_API_KEY = ""
            mock_settings.LLM_API_KEY = "some-key"
            mock_settings.SCRAPE_INTERVAL_MINUTES = 30
            mock_settings.SOURCES_CONFIG_PATH = "/fake/path"

            scrapers = load_all_scrapers()

        ids = [s["id"] for s in scrapers]
        assert "web_test_web" not in ids

    def test_loads_web_source_with_llm_settings(self, monkeypatch):
        config = {
            "api_sources": [],
            "web_sources": [{
                "name": "test_web",
                "enabled": True,
                "alert_type": "test",
                "url": "http://example.com",
            }],
        }

        monkeypatch.setattr("scrapers.registry._load_yaml_config", lambda: config)
        monkeypatch.setattr("scrapers.registry.WebScraper", lambda cfg: {"config": cfg})
        monkeypatch.setattr("scrapers.registry.settings.FIRECRAWL_API_KEY", "firecrawl-key")
        monkeypatch.setattr("scrapers.registry.settings.LLM_PROVIDER", "openrouter")
        monkeypatch.setattr("scrapers.registry.settings.LLM_API_KEY", "llm-key")

        scrapers = load_all_scrapers()

        ids = [s["id"] for s in scrapers]
        assert "web_test_web" in ids
