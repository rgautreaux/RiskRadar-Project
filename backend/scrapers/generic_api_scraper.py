"""Config-driven REST API scraper.

Instantiated once per entry in sources.yaml -> api_sources.
Inherits BaseScraper so run(), dedup, and ScrapeLog work unchanged.
"""

import csv
import io
import logging
import os
from datetime import date, timedelta
from typing import Any

import httpx

from config.settings import settings
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


def _build_template_vars() -> dict[str, str]:
    """Template variables available in config strings like '{today}'."""
    today = date.today()
    return {
        "today": today.isoformat(),
        "today_minus_1": (today - timedelta(days=1)).isoformat(),
        "today_minus_7": (today - timedelta(days=7)).isoformat(),
        "default_lat": str(settings.DEFAULT_LAT),
        "default_lon": str(settings.DEFAULT_LON),
        "default_zip": settings.DEFAULT_ZIP_CODE,
    }


def _resolve_template(value: Any, template_vars: dict[str, str]) -> Any:
    """Replace {placeholder} strings in config values."""
    if isinstance(value, str):
        for key, replacement in template_vars.items():
            value = value.replace(f"{{{key}}}", replacement)
    return value


def _extract_path(obj: Any, path: str) -> Any:
    """Traverse a nested dict/list using dot notation.

    Examples: "properties.title", "geometry.coordinates[1]", "data.alerts"
    """
    if not path:
        return obj
    for segment in path.split("."):
        if "[" in segment:
            field, idx_str = segment.rstrip("]").split("[")
            obj = obj[field][int(idx_str)]
        elif isinstance(obj, (list, tuple)) and segment.isdigit():
            obj = obj[int(segment)]
        else:
            # Support bare integer indices for list traversal (e.g. items_path: "1")
            try:
                obj = obj[int(segment)]
            except (ValueError, TypeError):
                obj = obj[segment]
    return obj


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class GenericAPIScraper(BaseScraper):
    """A single instance handles one api_sources config entry."""

    def __init__(self, config: dict):
        self._config = config
        self.source_name = config["name"]
        self.alert_type = config["alert_type"]

    def fetch_raw_data(self) -> list[dict]:
        tpl = _build_template_vars()
        cfg = self._config
        req = cfg.get("request", {})

        # Build params with template expansion
        params = {
            k: _resolve_template(v, tpl)
            for k, v in (req.get("params") or {}).items()
        }
        headers = dict(req.get("headers") or {})

        # Auth
        auth_cfg = cfg.get("auth", {})
        auth_type = auth_cfg.get("type", "none")
        if auth_type != "none":
            env_var = auth_cfg["env_var"]
            key_value = os.environ.get(env_var, "").strip() or str(getattr(settings, env_var, "")).strip()
            if not key_value:
                raise RuntimeError(
                    f"{self.source_name}: env var {env_var} not set"
                )
            if auth_type == "query_param":
                param_name = auth_cfg.get("param_name", "api_key")
                params[param_name] = key_value
            elif auth_type == "header":
                header_name = auth_cfg.get("header_name", "X-Api-Key")
                headers[header_name] = key_value
            elif auth_type == "bearer":
                headers["Authorization"] = f"Bearer {key_value}"

        url = cfg["url"]
        method = cfg.get("method", "GET").upper()
        resp = httpx.request(method, url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()

        # Parse response
        resp_cfg = cfg.get("response", {})
        fmt = resp_cfg.get("format", "json")

        if fmt == "csv":
            reader = csv.DictReader(io.StringIO(resp.text))
            return list(reader)
        else:  # json (default)
            data = resp.json()
            items_path = resp_cfg.get("items_path")
            if items_path:
                data = _extract_path(data, items_path)
            if isinstance(data, dict):
                data = [data]
            return data

    def normalize(self, raw: dict) -> dict:
        mapping = self._config["field_mapping"]

        def _get(path_or_val):
            if path_or_val is None:
                return None
            if path_or_val == "__full_item__":
                return raw
            try:
                return _extract_path(raw, path_or_val)
            except (KeyError, IndexError, TypeError):
                return None

        return {
            "source": self.source_name,
            "source_id": str(_get(mapping.get("source_id")) or ""),
            "alert_type": self.alert_type,
            "severity": self._compute_severity(raw),
            "title": str(_get(mapping.get("title")) or f"{self.source_name} alert"),
            "description": str(_get(mapping.get("description")) or ""),
            "raw_data": _get(mapping.get("raw_data", "__full_item__")),
            "latitude": _safe_float(_get(mapping.get("latitude"))),
            "longitude": _safe_float(_get(mapping.get("longitude"))),
            "location_name": str(_get(mapping.get("location_name")) or ""),
            "event_start": _get(mapping.get("event_start")),
            "event_end": _get(mapping.get("event_end")),
        }

    def _compute_severity(self, raw: dict) -> str:
        sev_cfg = self._config.get("severity", {})
        sev_type = sev_cfg.get("type", "fixed")

        if sev_type == "fixed":
            return sev_cfg.get("value", "moderate")

        field_val = None
        try:
            field_val = _extract_path(raw, sev_cfg["field"])
        except (KeyError, IndexError, TypeError):
            return sev_cfg.get("default", "moderate")

        if sev_type == "mapping":
            mapping = sev_cfg.get("map", {})
            return mapping.get(str(field_val), sev_cfg.get("default", "moderate"))

        if sev_type == "threshold":
            try:
                numeric_val = float(field_val)
            except (TypeError, ValueError):
                return sev_cfg.get("default", "moderate")
            for rule in sev_cfg.get("thresholds", []):
                if "gte" in rule and numeric_val >= rule["gte"]:
                    return rule["value"]
                if "lte" in rule and numeric_val <= rule["lte"]:
                    return rule["value"]
                if "default" in rule:
                    return rule["default"]

        return "moderate"
