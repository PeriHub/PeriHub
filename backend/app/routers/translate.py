# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import time

import paramiko
from fastapi import APIRouter, Request
from gcodereader import gcodereader

from support.base_models import ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/translate", tags=["Translate Methods"])


@router.post("/model")
def translate_model(
    model_name: str,
    file_type: str,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    start_time = time.time()

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    inputformat = "'ansys (cdb)'"
    if file_type == "cdb":
        inputformat = "ansys"
    if file_type == "inp":
        inputformat = "abaqus"
        # inputformat = "'ansys (cdb)'"

    command = (
        "java -jar ./support/jCoMoT/jCoMoT-0.0.1-all.jar -ifile "
        + os.path.join(localpath, model_name + "." + file_type)
        + " -iformat "
        + inputformat
        + " -oformat peridigm -opath "
        + localpath
    )  # + \
    # " && mv " + os.path.join(localpath, 'mesh.g.ascii ') + os.path.join(localpath, model_name) + '.g.ascii' + \
    # " && mv " + os.path.join(localpath, 'model.peridigm ') + os.path.join(localpath, model_name) + '.peridigm'
    # " && mv " + os.path.join(localpath, 'discretization.g.ascii ') + os.path.join(localpath, model_name)
    # + '.g.ascii' + \
    try:
        subprocess.call(command, shell=True)
    except subprocess.SubprocessError:
        log.error("%s results can not be found", model_name)
        return "%s results can not be found", model_name

    log.info("Rename mesh File")
    os.rename(
        os.path.join(localpath, "mesh.g.ascii"),
        os.path.join(localpath, model_name + ".g.ascii"),
    )
    log.info("Rename peridigm File")
    os.rename(
        os.path.join(localpath, "model.peridigm"),
        os.path.join(localpath, model_name + ".peridigm"),
    )

    log.info("Copy mesh File")
    if (
        FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".g.ascii", True)
        != "Success"
    ):
        log.error("%s can not be translated", model_name)
        return "%s can not be translated", model_name

    log.info("Copy peridigm File")
    if (
        FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".peridigm", True)
        != "Success"
    ):
        log.error("%s can not be translated", model_name)
        return "%s can not be translated", model_name

    # if return_string!='Success':
    #     return return_string

    server = "perihub_peridigm"
    remotepath = "/app/peridigmJobs/" + os.path.join(username, model_name)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(
            server,
            username="root",
            allow_agent=False,
            password="root",
        )
    except paramiko.SSHException:
        log.error("ssh connection to %s failed!", server)
        return "ssh connection to " + server + " failed!"
    command = (
        "/usr/local/netcdf/bin/ncgen "
        + os.path.join(remotepath, model_name)
        + ".g.ascii -o "
        + os.path.join(remotepath, model_name)
        + ".g"
        + " && python3 /peridigm/scripts/peridigm_to_yaml.py "
        + os.path.join(remotepath, model_name)
        + ".peridigm"
        + " && rm "
        + os.path.join(remotepath, model_name)
        + ".peridigm"
    )
    # ' && rm ' +  os.path.join(remotepath, model_name) + '.g.ascii' + \
    log.info("Peridigm to yaml")
    _, stdout, _ = ssh.exec_command(command)
    stdout.channel.set_combine_stderr(True)
    # output = stdout.readlines()
    ssh.close()

    log.info("Copy mesh File")
    FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".g", False)
    log.info("Copy yaml File")
    FileHandler.copy_file_to_from_peridigm_container(username, model_name, model_name + ".yaml", False)

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
