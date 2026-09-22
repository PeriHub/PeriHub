# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, HTTPException

from ..support import runtime_settings
from ..support.base_models import SettingInfo, SettingsResponse, SettingsUpdateRequest
from ..support.globals import ENV_LOCKED_KEYS

router = APIRouter(prefix="/settings", tags=["Settings Methods"])


def _response() -> SettingsResponse:
    return SettingsResponse(settings=[SettingInfo(**s) for s in runtime_settings.list_settings(ENV_LOCKED_KEYS)])


@router.get("/", operation_id="get_settings")
def get_settings() -> SettingsResponse:
    """Every env-var-backed configuration value from support/globals.py,
    with its current value and whether it can be edited here.

    A setting is read-only whenever it's already provided by the real
    process environment (docker `env_file`/`environment:`, or a real `.env`
    file) - a value saved from this dialog is only ever allowed to fill in a
    setting nobody has explicitly configured, never override one that has.
    `secret`-typed settings (passwords, API keys, the license key) never
    have their actual value sent to the client, only whether one is set.

    NOTE: unauthenticated for now, matching the rest of this router set (see
    the security roadmap item on trusted-header auth). Before exposing this
    beyond a single trusted operator, writing to it should be gated the same
    way the eventual admin-only endpoints are, since several of these
    settings (cluster credentials, the license key, API keys) are secrets.
    """
    return _response()


@router.put("/", operation_id="update_settings")
def update_settings(body: SettingsUpdateRequest) -> SettingsResponse:
    """Persists new values for the given (editable) settings so they're
    picked up the next time the backend process starts - see
    support/runtime_settings.py for why this can't take effect immediately
    for most of them. Raises 400 for an unknown key or an invalid value, and
    403 if any key in the request is locked by the real environment."""
    try:
        runtime_settings.update_settings(body.values, ENV_LOCKED_KEYS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return _response()
