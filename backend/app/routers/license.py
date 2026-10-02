# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends

from ..support import license_client
from ..support.base_models import LicenseStatus
from .admin import require_admin

router = APIRouter(prefix="/license", tags=["License Methods"])


@router.get("/status", operation_id="get_license_status")
def get_license_status() -> LicenseStatus:
    """Current plan and unlocked features for this instance. Safe to expose
    to any authenticated user (it doesn't reveal the license key itself) -
    the frontend plan/upgrade dialog reads from this."""
    return license_client.get_status()


@router.post("/refresh", operation_id="refresh_license", dependencies=[Depends(require_admin)])
def refresh_license() -> LicenseStatus:
    """Force an immediate re-check against the license server instead of
    waiting for the normal refresh interval - useful right after a plan
    change, or for ops to confirm a new license key was picked up.

    Admins only, so nobody else can put needless load on the license server.
    """
    return license_client.get_status(force_refresh=True)
