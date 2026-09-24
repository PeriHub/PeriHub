# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Public, unauthenticated deployment config for the frontend.

Before this, the frontend duplicated TRIAL/CLUSTER_URL as its own VITE_*
env vars (see src/lib/config.ts), baked into the build or substituted into
the compiled JS at container startup (entrypoint.sh) - the same values had
to be set twice, once for the backend and once for the frontend container,
with nothing keeping them in sync. This endpoint is the single source of
truth: the backend already has these in support/globals.py, so the
frontend just asks for them at startup (src/lib/config.ts's
loadPublicConfig()) instead of carrying its own copies.

Nothing sensitive is returned here: whether OAuth/OIDC login is currently
enabled is meant to be public (that's how the browser-side "log in" flow
decides whether to kick off at all), and no client id/secret or discovery
URL is ever included - the frontend never talks to the IdP directly, it
only calls PeriHub's own /oauth/oidc/login and /oauth/oidc/callback.
"""

from fastapi import APIRouter

from ..support.entitlements import has_feature
from ..support.globals import (
    cluster_enabled,
    cluster_url,
    deployment_mode,
    oauth_discovery_url,
)

router = APIRouter(prefix="/config", tags=["Config Methods"])


@router.get("/public", operation_id="get_public_config")
def get_public_config() -> dict:
    return {
        "deployment_mode": deployment_mode,
        "trial": deployment_mode == "trial",
        "cluster_url": cluster_url if cluster_enabled else "",
        # Only advertise OAuth login to the frontend if it's both
        # configured AND actually licensed - a community/trial deployment
        # that happens to have OAUTH_DISCOVERY_URL set (e.g. copied from an
        # old .env) still shouldn't get an SSO login screen, matching the
        # enterprise-only gating on the /oauth/oidc/* routes themselves.
        "oauth_enabled": bool(oauth_discovery_url) and has_feature("oauth_login"),
    }
