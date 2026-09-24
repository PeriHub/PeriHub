# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""API-key auth for programmatic/CI callers.

FileHandler.get_user_name() identifies a user from the `userName` header,
which the frontend sets after an OAuth/OIDC login (or a random guest name in
trial/dev mode). That's fine for browser sessions but awkward for CI or
server-to-server callers that have no browser session at all.

This adds an *optional*, additive check: if the caller sends a valid
`X-Api-Key` header, the configured name for that key is used as the
username instead of whatever get_user_name() resolved (browser header,
guest fallback, etc). If the project's API_KEYS setting isn't configured,
or the header isn't present, this is a no-op and the original username is
returned unchanged - i.e. this cannot make an unauthenticated request
*more* trusted than before, only give already-privileged automation a
stable identity instead of "user"/a random guest name.

NOTE: this is a shared-secret scheme sent as a plain header, so it only
provides real protection over HTTPS; it is not a substitute for the
OAuth/OIDC login flow for interactive/browser users.
"""

from fastapi import Request

from .globals import api_keys_raw


def _parse_api_keys() -> dict[str, str]:
    """Parses API_KEYS="name:key,name2:key2" into {key: name}."""
    keys: dict[str, str] = {}
    for pair in api_keys_raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        name, _, key = pair.partition(":")
        name, key = name.strip(), key.strip()
        if name and key:
            keys[key] = name
    return keys


# Parsed once at import time; API_KEYS is only read from the environment at
# process startup anyway (see support/globals.py), so there's no need to
# re-parse this on every request.
_API_KEYS = _parse_api_keys()


def get_user_name_with_api_key(request: Request, dev: bool, fallback_username: str) -> str:
    """Returns the username associated with a valid X-Api-Key header, or
    `fallback_username` (the result of FileHandler.get_user_name()) if no
    key is configured/presented/valid.

    `dev` is currently unused but kept in the signature to match every call
    site (`get_user_name_with_api_key(request, dev, username)`); it's a
    natural hook if dev-mode ever needs to bypass key validation.
    """
    del dev
    if not _API_KEYS:
        return fallback_username

    api_key = request.headers.get("X-Api-Key")
    if not api_key:
        return fallback_username

    return _API_KEYS.get(api_key, fallback_username)
