# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import time

from fastapi import APIRouter, Request
from gcodereader import gcodereader

from support.base_models import ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log, trial

router = APIRouter(prefix="/translate", tags=["Translate Methods"])


@router.post("/model")
def translate_model(
    file: str,
    model_name: str,
    model_folder_name: str = "Default",
    discretization: float = 2,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    start_time = time.time()

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    model_file = os.path.join(localpath, file)

    timeout = 300
    print(trial)
    if trial:
        timeout = 10
    try:
        result = subprocess.run(
            [
                "python",
                "./support/model/meshing.py",
                "--model_file",
                model_file,
                "--discretization",
                str(discretization),
                "--localpath",
                localpath,
                "--model_name",
                model_name,
            ],
            timeout=timeout,
        )  # Set the timeout to 60 seconds
    except subprocess.TimeoutExpired:
        log.info(
            "%s took too long. %.2f seconds",
            model_name,
            time.time() - start_time,
        )
        return ResponseModel(
            data=False,
            message=f"{model_name} took too long. Try to increase the discretization parameter",
        )
        # Add code here to handle the timeout, such as terminating the process or raising an exception

    log.info(
        "%s has been translated in %.2f seconds",
        model_name,
        time.time() - start_time,
    )
    return ResponseModel(
        data=True,
        message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
    )


@router.post("/gcode")
async def translate_gcode(
    model_name: str,
    discretization: float,
    dt: float,
    scale: float,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    start_time = time.time()

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)
    # output_path = FileHandler.get_local_user_path(username)

    gcodereader.read(model_name, localpath, localpath, discretization, dt, scale)

    log.info(
        "%s has been translated in %.2f seconds",
        model_name,
        time.time() - start_time,
    )
    return ResponseModel(
        data=True,
        message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
    )
