# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

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


@router.delete("/modelFromCluster", operation_id="delete_model_from_cluster")
def delete_model_from_cluster(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
    if not cluster:
        if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
        audit_log.record(username, "delete_model_from_cluster", model_name, request, extra={"cluster": False})
        log.info("%s has been deleted", model_name)
        return
    ssh, sftp = FileHandler.sftp_to_cluster(cluster)

    for filename in sftp.listdir(remotepath):
        sftp.remove(os.path.join(remotepath, filename))
    sftp.rmdir(remotepath)
    sftp.close()
    ssh.close()

    audit_log.record(username, "delete_model_from_cluster", model_name, request, extra={"cluster": True})


@router.delete("/userData", operation_id="delete_user_data")
def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
    """doc"""
    if check_date:
        localpath = FileHandler.get_local_simulation_path()
        if os.path.exists(localpath):
            names = FileHandler.remove_folder_if_older(localpath, days, True)
            if len(names) != 0:
                audit_log.record(
                    "system", "delete_user_data_by_age", ", ".join(names), request, extra={"days": days}
                )
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


@router.delete("/userDataFromCluster", operation_id="delete_user_data_from_cluster")
def delete_user_data_from_cluster(
    cluster: bool,
    check_date: bool,
    request: Request,
    days: Optional[int] = 7,
):
    """doc"""

    if check_date:
        if not cluster:
            localpath = FileHandler.get_local_simulation_path()
            names = FileHandler.remove_folder_if_older(localpath, days, True)
        else:
            remotepath = FileHandler.get_remote_path(cluster)

            ssh, sftp = FileHandler.sftp_to_cluster(cluster)

            names = FileHandler.remove_folder_if_older_sftp(sftp, remotepath, days, True)

            sftp.close()
            ssh.close()

        audit_log.record(
            "system",
            "delete_user_data_from_cluster_by_age",
            str(names),
            request,
            extra={"cluster": cluster, "days": days},
        )
        log.info("Data of %s has been deleted", names)
        return

    username = FileHandler.get_user_name(request, dev)
    username = get_user_name_with_api_key(request, dev, username)

    if not cluster:
        # NOTE: get_remote_user_path() requires the username argument - the
        # original code called it with none, which would have raised a
        # TypeError for every non-cluster, non-check_date call here.
        remotepath = FileHandler.get_remote_user_path(username)
        if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
        audit_log.record(username, "delete_user_data_from_cluster", username, request, extra={"cluster": False})
        log.info("Data of %s has been deleted", username)
        return

    remotepath = FileHandler.get_remote_user_path(username)

    ssh, sftp = FileHandler.sftp_to_cluster(cluster)

    FileHandler.remove_all_folder_ssh(ssh, remotepath)

    sftp.close()
    ssh.close()

    audit_log.record(username, "delete_user_data_from_cluster", username, request, extra={"cluster": True})
    log.info("Data of %s has been deleted", username)
