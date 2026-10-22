# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests

from backend.app.support import license_client


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


@pytest.fixture
def server(monkeypatch, tmp_path):
    """POST /api/v1/validate answering `server.payload` (an exception instance = unreachable)."""
    calls = []
    state = type("S", (), {"payload": None, "calls": calls})()

    def post(url, json, timeout):
        calls.append((url, json))
        if isinstance(state.payload, Exception):
            raise state.payload
        return _Response(state.payload)

    monkeypatch.setattr(license_client.requests, "post", post)
    monkeypatch.setattr(license_client, "license_server_url", "https://lic.example.com/")
    monkeypatch.setattr(license_client, "license_key", "KEY")
    monkeypatch.setattr(license_client, "license_instance_id", "PeriHub_Dev")
    monkeypatch.setattr(license_client, "license_cache_path", str(tmp_path / "cache.json"))
    return state


def test_valid_license_unlocks_features(server):
    server.payload = {"valid": True, "features": ["oauth_login"], "expires_at": "2027-01-01T00:00:00"}
    status = license_client.get_status(force_refresh=True)
    assert (status.plan, status.features, status.seats, status.source) == (
        "enterprise",
        ["oauth_login"],
        None,
        "license_server",
    )
    assert server.calls == [
        ("https://lic.example.com/api/v1/validate", {"license_key": "KEY", "machine_id": "PeriHub_Dev"})
    ]
    assert license_client.get_status().source == "cache"  # no second call within the refresh interval
    assert len(server.calls) == 1


def test_invalid_license_is_final_not_an_outage(server):
    server.payload = {"valid": True, "features": ["oauth_login"]}
    license_client.get_status(force_refresh=True)
    # revoked: community straight away, even though a fresh-enough cached grant exists
    server.payload = {"valid": False, "reason": "revoked"}
    status = license_client.get_status(force_refresh=True)
    assert (status.plan, status.features) == ("community", [])


def test_unreachable_server_keeps_cached_grant(server):
    server.payload = {"valid": True, "features": ["oauth_login"]}
    license_client.get_status(force_refresh=True)
    server.payload = requests.ConnectionError("down")
    status = license_client.get_status(force_refresh=True)
    assert (status.features, status.source) == (["oauth_login"], "cache")
