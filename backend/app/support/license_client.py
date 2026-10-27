"""Client for the PeriHub license server (Phase 1).

If LICENSE_SERVER_URL isn't configured, everything in this module degrades
to the open-core default (plan="community", no gated features) rather than
failing; PeriHub is fully usable with zero license-server configuration.

Contract - the same call PeriLab's ModuleLoader makes, so the server has one
license check (adjust this module, not the callers in support/entitlements.py,
if it changes):

    POST {LICENSE_SERVER_URL}/api/v1/validate
    {"license_key": LICENSE_KEY, "machine_id": LICENSE_INSTANCE_ID}
    200 OK:
        {"valid": true, "features": ["oauth_login", ...], "expires_at": "2027-01-01T00:00:00", ...}
        {"valid": false, "reason": "unknown license key" | "expired" | "revoked" | "activation limit reached"}

Mapping: a valid license is plan "enterprise", an invalid one "community" -
that's a definitive answer and is cached like any other, not treated as an
outage. The server has no user-seat count (max_activations counts machines:
this backend is one activation, the PeriLab container another), so `seats`
stays None = no per-org user limit.

Caching / offline behaviour:
- A successful response is cached to disk (LICENSE_CACHE_PATH) and reused
  for LICENSE_REFRESH_INTERVAL_SECONDS before the next network call, so
  every request that checks an entitlement doesn't hit the license server.
- If the license server is unreachable, the last-known-good cached grant
  keeps being honoured for up to LICENSE_OFFLINE_GRACE_PERIOD_SECONDS after
  it was fetched, so a transient outage doesn't immediately revoke paid
  features from a customer who is otherwise in good standing. After the
  grace period expires with no successful refresh, this falls back to the
  community default until the license server is reachable again.
"""

import json
import os
import socket
import threading
import time
from typing import Optional

import requests

from .base_models import LicenseStatus
from .globals import (
    license_cache_path,
    license_instance_id,
    license_key,
    license_offline_grace_period_seconds,
    license_refresh_interval_seconds,
    license_server_url,
    log,
)

_lock = threading.Lock()
_DEFAULT = LicenseStatus(
    plan="community",
    features=[],
    seats=None,
    expires_at=None,
    source="default",
    license_server_configured=bool(license_server_url),
)


def _load_cache() -> Optional[dict]:
    if not os.path.exists(license_cache_path):
        return None
    try:
        with open(license_cache_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(status: LicenseStatus, fetched_at: float) -> None:
    try:
        os.makedirs(os.path.dirname(license_cache_path), exist_ok=True)
        with _lock:
            with open(license_cache_path, "w", encoding="utf-8") as f:
                json.dump({"fetched_at": fetched_at, "status": status.model_dump()}, f)
    except OSError as exc:
        log.warning("license_client: failed to write cache: %s", exc)


def _fetch_from_server() -> Optional[LicenseStatus]:
    """The server's answer, valid or not; None only if it couldn't be reached (then the cache grace applies)."""
    if not license_server_url:
        return None
    machine_id = license_instance_id or socket.gethostname()
    if not license_instance_id:
        # A recreated container gets a new hostname, i.e. a new activation each time - set LICENSE_INSTANCE_ID.
        log.warning("license_client: LICENSE_INSTANCE_ID not set, using hostname %s as machine id", machine_id)
    try:
        response = requests.post(
            f"{license_server_url.rstrip('/')}/api/v1/validate",
            json={"license_key": license_key, "machine_id": machine_id},
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        log.warning("license_client: could not reach license server: %s", exc)
        return None
    if not payload.get("valid"):
        log.warning("license_client: license not valid (%s), using community plan", payload.get("reason"))
        return LicenseStatus(**{**_DEFAULT.model_dump(), "source": "license_server"})
    return LicenseStatus(
        plan="enterprise",
        features=payload.get("features") or [],
        seats=None,
        expires_at=payload.get("expires_at"),
        source="license_server",
        license_server_configured=True,
    )


def get_status(force_refresh: bool = False) -> LicenseStatus:
    """Returns the current entitlement grant, fetching from the license
    server if the cache is stale (or `force_refresh` is set), and falling
    back to cache/community as described in this module's docstring."""
    if not license_server_url:
        return _DEFAULT

    cache = _load_cache()
    now = time.time()
    cache_is_fresh = cache is not None and (now - cache["fetched_at"]) < license_refresh_interval_seconds

    if cache_is_fresh and not force_refresh:
        status = LicenseStatus(**cache["status"])
        status.source = "cache"
        return status

    fetched = _fetch_from_server()
    if fetched is not None:
        _save_cache(fetched, now)
        return fetched

    # Server unreachable: honour a stale cache within the offline grace period.
    if cache is not None and (now - cache["fetched_at"]) < license_offline_grace_period_seconds:
        status = LicenseStatus(**cache["status"])
        status.source = "cache"
        log.warning("license_client: using stale cached entitlements (server unreachable)")
        return status

    log.warning("license_client: no valid license grant available, falling back to community plan")
    return _DEFAULT
