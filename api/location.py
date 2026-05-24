from importlib import import_module

_impl = import_module("backend.api.location")

for _name in (
    "router",
    "get_alerts_for_location",
    "search_location",
    "autocomplete_location",
    "get_location_info",
    "_zip_to_coords",
    "_fetch_nws_alerts",
    "_fetch_airnow",
    "_fetch_pollen",
    "SEVERITY_MAP",
):
    globals()[_name] = getattr(_impl, _name)
