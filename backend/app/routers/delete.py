# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import Optional

from fastapi import APIRouter, Request

# from ..support.base_models import
from ..support import audit_log
from ..support.api_key_auth import get_user_name_with_api_key
from ..support.file_handler import FileHandler
from ..support.globals import dev, log

router = APIRouter(prefix="/delete", tags=["Delete Methods"])


@router.delete("/model", operation_id="delete_model")
def delete_model(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
    if os.path.exists(localpath):
        shutil.rmtree(localpath)
    audit_log.record(username, "delete_model", model_name, request, extra={"model_folder_name": model_folder_name})
    log.info("%s has been deleted", model_name)


@router.delete("/userData", operation_id="delete_user_data")
def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
    """doc"""
    if check_date:
        localpath = FileHandler.get_local_simulation_path()
        if os.path.exists(localpath):
            names = FileHandler.remove_folder_if_older(localpath, days, True)
            if len(names) != 0:
                audit_log.record("system", "delete_user_data_by_age", ", ".join(names), request, extra={"days": days})
                log.info("Data of %s has been deleted", ", ".join(names))
                return "Data of " + ", ".join(names) + " has been deleted"
        log.info("Nothing has been deleted")
        return

    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    # NOTE: get_local_user_path() requires the username argument - the
    # original code called it with none, which would have raised a TypeError
    # for every non-check_date call to this endpoint.
    localpath = FileHandler.get_local_user_path(username)
    if os.path.exists(localpath):
        shutil.rmtree(localpath)
    audit_log.record(username, "delete_user_data", username, request)
    log.info("Data of %s has been deleted", username)
