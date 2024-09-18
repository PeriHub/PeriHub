# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from ..support.base_models import ResponseModel
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

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)
    if os.path.exists(localpath):
        shutil.rmtree(localpath)
    log.info("%s has been deleted", model_name)
    return ResponseModel(data=True, message=model_name + " has been deleted")


@router.delete("/modelFromCluster", operation_id="delete_model_from_cluster")
def delete_model_from_cluster(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)
    if not cluster:
        if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
        log.info("%s has been deleted", model_name)
        return ResponseModel(data=True, message=model_name + " has been deleted")

    ssh, sftp = FileHandler.sftp_to_cluster(cluster)

    for filename in sftp.listdir(remotepath):
        sftp.remove(os.path.join(remotepath, filename))
    sftp.rmdir(remotepath)
    sftp.close()
    ssh.close()
    log.info("%s has been deleted", model_name)
    return ResponseModel(data=True, message=model_name + " has been deleted")


@router.delete("/userData", operation_id="delete_user_data")
def delete_user_data(check_date: bool, request: Request, days: Optional[int] = 7):
    """doc"""
    if check_date:
        localpath = "./simulations"
        if os.path.exists(localpath):
            names = FileHandler.remove_folder_if_older(localpath, days, True)
            if len(names) != 0:
                log.info("Data of %s has been deleted", ", ".join(names))
                return "Data of " + ", ".join(names) + " has been deleted"
        log.info("Nothing has been deleted")
        return ResponseModel(data=True, message="Nothing has been deleted")

    username = FileHandler.get_user_name(request, dev)

    localpath = "./simulations/" + username
    if os.path.exists(localpath):
        shutil.rmtree(localpath)
    log.info("Data of %s has been deleted", username)
    return ResponseModel(data=True, message="Data of " + username + " has been deleted")


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
            localpath = "./simulations"
            names = FileHandler.remove_folder_if_older(localpath, days, True)
        else:
            remotepath = FileHandler.get_remote_path(cluster)

            ssh, sftp = FileHandler.sftp_to_cluster(cluster)

            names = FileHandler.remove_folder_if_older_sftp(sftp, remotepath, days, True)

            sftp.close()
            ssh.close()

        log.info("Data of %s has been deleted", names)
        return ResponseModel(data=True, message="Data of " + names + " has been deleted")

    username = FileHandler.get_user_name(request, dev)

    if not cluster:
        remotepath = "./simulations/" + username
        if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
        log.info("Data of %s has been deleted", username)
        return ResponseModel(data=True, message="Data of " + username + " has been deleted")

    remotepath = FileHandler.get_remote_user_path(username)

    ssh, sftp = FileHandler.sftp_to_cluster(cluster)

    FileHandler.remove_all_folder_ssh(ssh, remotepath)

    sftp.close()
    ssh.close()

    log.info("Data of %s has been deleted", username)
    return ResponseModel(data=True, message="Data of " + username + " has been deleted")
