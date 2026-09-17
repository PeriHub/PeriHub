# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Request

from ..support import usage_metering
from ..support.api_key_auth import get_user_name_with_api_key
from ..support.base_models import UsageSummary
from ..support.file_handler import FileHandler
from ..support.globals import dev

router = APIRouter(prefix="/usage", tags=["Usage Methods"])


@router.get("/me", operation_id="get_my_usage")
def get_my_usage(request: Request) -> UsageSummary:
    """Usage summary (jobs submitted/cancelled, cluster vs local, per model)
    scoped to the calling user."""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)
    return usage_metering.get_usage_for_user(username)


@router.get("/all", operation_id="get_all_usage")
def get_all_usage() -> UsageSummary:
    """Instance-wide usage summary.

    NOTE: unauthenticated/unrestricted for now, matching the rest of this
    router set. Before exposing this beyond a trusted operator, it should be
    gated the same way the admin/audit-log endpoints eventually are (see the
    security and licensing roadmap items) so one user can't see another
    tenant's aggregate usage.
    """
    return usage_metering.get_all_usage()
