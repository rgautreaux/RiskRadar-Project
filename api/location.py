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

# To allow tests to monkeypatch `api.location._fetch_nws_alerts` (and friends)
# and have the backend routes pick up those patches, install dynamic proxy
# callables on the backend implementation that delegate to the current value
# on this top-level module. This way tests can patch `api.location._fetch_*`
# and the backend route (which is registered from the backend module) will
# call through to the patched function.
def _proxy(name):
    def _fn(*a, **kw):
        mod = import_module("api.location")
        target = getattr(mod, name)
        return target(*a, **kw)

    return _fn

_proxy_names = ("_zip_to_coords", "_fetch_nws_alerts", "_fetch_airnow", "_fetch_pollen")
for _pname in _proxy_names:
    try:
        setattr(_impl, _pname, _proxy(_pname))
    except Exception:
        # Best-effort only; if this fails the original binding remains.
        pass
