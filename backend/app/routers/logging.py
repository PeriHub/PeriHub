# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from re import match

import paramiko
from fastapi import APIRouter, HTTPException, Query, WebSocket, status

from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/log")


async def log_reader(cluster, remotepath, file, software):
    log_lines = []

    if cluster == "None":
        log_file = os.path.join(remotepath, file)

        # log.info("log_file: %s", log_file)
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                for line in file.readlines()[-100:]:
                    log_lines.append(line)
        else:
            log_lines = ["No Logfile"]
    else:
        ssh, sftp = FileHandler.sftp_to_cluster(cluster, software)
        sftp.chdir(remotepath)
        file = sftp.file(file, "r")
        for line in file.readlines()[-100:]:
            log_lines.append(line)
        sftp.close()
        ssh.close()

    return log_lines


@router.websocket("/")
async def websocket_endpoint_log(
    websocket: WebSocket,
    model_name: str = Query(...),
    model_folder_name: str = "Default",
    cluster: str = Query(...),
    token: str = Query(...),
    software: str = "Peridigm",
):
    await websocket.accept()
    username = FileHandler.get_user_name_from_token(token, dev[0])

    if model_folder_name == "undefined":
        model_folder_name = "Default"
    if cluster == "None":
        remotepath = "./peridigmJobs/" + os.path.join(username, model_name, model_folder_name)
        try:
            output_files = os.listdir(remotepath)
            filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
        except IOError:
            log.error("LogFile can not be found in %s", remotepath)

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )
        if len(filtered_values) == 0:
            log.error("LogFile can not be found in %s", remotepath)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )

    else:
        remotepath = FileHandler.get_remote_model_path(username, model_name, model_folder_name)

        ssh, sftp = FileHandler.sftp_to_cluster(cluster, software)

        try:
            output_files = sftp.listdir(remotepath)
            filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
        except paramiko.SFTPError:
            log.error("LogFile can not be found in %s", remotepath)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )
        if len(filtered_values) == 0:
            log.error("LogFile can not be found in %s", remotepath)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LogFile can't be found in " + remotepath,
            )

    try:
        while True:
            await asyncio.sleep(1)
            logs = await log_reader(cluster, remotepath, filtered_values[-1])
            await websocket.send_text(logs)
    except Exception as e:
        print(e)
    finally:
        await websocket.close()
