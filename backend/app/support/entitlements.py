"""Feature gating on top of support/license_client.py.

Open-core model: every feature is available by default (an unconfigured
license server means `has_feature()` always returns True) so PeriHub works
fully without any license server set up. Gating only kicks in once
LICENSE_SERVER_URL is actually configured, at which point a feature must be
present in the current LicenseStatus.features list.

Gated features: "oauth_login" (ee/oauth.py) and "cluster_jobs" (Slurm
submission with the user's own cluster login, ee/cluster.py). Gating a new
feature is a one-line `require_feature()` at the relevant router.
"""

from fastapi import HTTPException, status

from .globals import license_server_url
from .license_client import get_status


def has_feature(feature: str) -> bool:
    if not license_server_url:
        return True  # open-core: no license server configured, nothing is gated
    return feature in get_status().features


def require_feature(feature: str) -> None:
    """Raises 402 Payment Required if `feature` isn't in the current plan.
    No-op (never raises) when no license server is configured."""
    if not has_feature(feature):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"'{feature}' requires a plan that includes it. See /license/status.",
        )
