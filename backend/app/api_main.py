# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from re import match

import paramiko
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import delete, docs, generate, jobs, model, results, translate, upload
from support.file_handler import FileHandler
from support.globals import dev, dlr, log

tags_metadata = [
    {
        "name": "Generate Methods",
        "description": "Generate models or mesh",
    },
    {"name": "Model Methods", "description": "Get model, points or input file"},
    {"name": "Upload Methods", "description": "Upload files"},
    {"name": "Translate Methods", "description": "Translate model or gcode"},
    {"name": "Jobs Methods", "description": "Run, cancel or write jobs"},
    {"name": "Results Methods", "description": "Get results"},
    {
        "name": "Delete Methods",
        "description": "Delete user or model data",
    },
    {
        "name": "Documentation Methods",
        "description": "Retrieve markdown documentation or bibtex files",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

origins = [
    "http://localhost",
    "http://localhost:6010",
    "http://localhost:8080",
    "https://localhost:6010",
    "https://perihub.fa-services.intra.dlr.de",
    "https://bpmn.nimbus.dlr.de",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(generate.router)
app.include_router(model.router)
app.include_router(upload.router)
app.include_router(translate.router)
app.include_router(jobs.router)
app.include_router(results.router)
app.include_router(delete.router)
app.include_router(docs.router)

load_dotenv()

dev[0] = os.getenv("DEV")
dlr[0] = os.getenv("DLR")
if dev[0] == "True":
    log.info("--- Running in development mode ---")
if dlr[0] == "True":
    log.info("--- Running in DLR mode ---")


async def log_reader(cluster, remotepath, file):
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
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        sftp.chdir(remotepath)
        file = sftp.file(file, "r")
        for line in file.readlines()[-100:]:
            log_lines.append(line)
        sftp.close()
        ssh.close()

    return log_lines


@app.websocket("/log")
async def websocket_endpoint_log(
    websocket: WebSocket,
    model_name: str = Query(...),
    model_folder_name: str = "Default",
    cluster: str = Query(...),
    token: str = Query(...),
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

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

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
