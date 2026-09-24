# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Generic OAuth2/OIDC login for enterprise customers not using Keycloak.

Standard authorization-code flow against any IdP that publishes an OIDC
discovery document at OAUTH_DISCOVERY_URL
(".../.well-known/openid-configuration"). Unlike the Keycloak path (which
only verifies a token the frontend already obtained), PeriHub itself drives
this exchange: routers/oauth.py's /oauth/oidc/login builds the redirect,
and /oauth/oidc/callback trades the returned `code` for tokens here.

State handling: the `state` parameter is generated and returned to the
caller in /oidc/login rather than stored server-side, since this is a
stateless API service. Whoever calls /oidc/login (the frontend) is
responsible for round-tripping it (e.g. sessionStorage) and PeriHub does
not re-verify it beyond passing it through - CSRF protection here relies on
the frontend actually checking the returned state matches on callback.
"""

import secrets
from urllib.parse import urlencode

import requests

from .globals import (
    log,
    oauth_client_id,
    oauth_client_secret,
    oauth_discovery_url,
    oauth_redirect_uri,
)

_discovery_cache: dict | None = None


def _discovery() -> dict:
    global _discovery_cache
    if _discovery_cache is None:
        response = requests.get(oauth_discovery_url, timeout=5)
        response.raise_for_status()
        _discovery_cache = response.json()
    return _discovery_cache


def build_authorization_url() -> tuple[str, str]:
    """Returns (authorization_url, state). Raises RuntimeError if OIDC isn't
    configured, requests.RequestException if the discovery document can't
    be fetched."""
    if not oauth_discovery_url or not oauth_client_id or not oauth_redirect_uri:
        raise RuntimeError("OAUTH_DISCOVERY_URL/OAUTH_CLIENT_ID/OAUTH_REDIRECT_URI are not configured.")
    doc = _discovery()
    state = secrets.token_urlsafe(24)
    params = {
        "response_type": "code",
        "client_id": oauth_client_id,
        "redirect_uri": oauth_redirect_uri,
        "scope": "openid email profile",
        "state": state,
    }
    query = urlencode(params)
    return f"{doc['authorization_endpoint']}?{query}", state


def exchange_code_for_userinfo(code: str) -> dict:
    """Exchanges an authorization `code` for tokens, then fetches and
    returns the userinfo claims (sub, email, preferred_username/name).
    Raises requests.RequestException on any HTTP failure."""
    doc = _discovery()
    token_response = requests.post(
        doc["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": oauth_redirect_uri,
            "client_id": oauth_client_id,
            "client_secret": oauth_client_secret,
        },
        timeout=5,
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    userinfo_response = requests.get(
        doc["userinfo_endpoint"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=5,
    )
    userinfo_response.raise_for_status()
    return userinfo_response.json()
