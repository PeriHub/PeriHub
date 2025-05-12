# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from re import match

import paramiko
from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import (
    delete,
    docs,
    energy,
    generate,
    jobs,
    model,
    results,
    translate,
    upload,
)
from .support.file_handler import FileHandler
from .support.globals import dev, log, trial

tags_metadata = [
    {
        "name": "Generate Methods",
        "description": "Generate models or mesh",
    },
    {"name": "Model Methods", "description": "Get model, points or input file"},
    {"name": "Upload Methods", "description": "Upload files"},
    {"name": "Translate Methods", "description": "Translate model or gcode"},
    {"name": "Jobs Methods", "description": "Run, cancel or write jobs"},
    {"name": "simulations Methods", "description": "Get results"},
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

origins = ["*"]

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
app.include_router(energy.router)

if dev:
    log.info("--- Running in development mode ---")
if trial:
    log.info("--- Running in trial mode ---")


@app.get("/health")
async def healthcheck():
    return {"status": True}


async def log_reader(cluster, log_file, debug):
    log_lines = []

    if not cluster:
        # log.info("log_file: %s", log_file)
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                for line in file.readlines():
                    if not debug and "[Debug]" in line:
                        continue
                    log_lines.append(line)
        else:
            log_lines = ["No Logfile"]
    else:
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
        file = sftp.file(log_file, "r")
        for line in file.readlines():
            if not debug and "[Debug]" in line:
                continue
            log_lines.append(line)
        sftp.close()
        ssh.close()

    return log_lines


@app.websocket("/ws")
async def websocket_endpoint_log(
    websocket: WebSocket,
    model_name: str = Query(...),
    model_folder_name: str = "Default",
    cluster: bool = Query(...),
    token: str = Query(...),
    user_name: str = Query(...),
    debug: bool = Query(...),
):
    await websocket.accept()

    username = user_name
    if user_name == None or user_name == "" or user_name == "undefined":
        username = FileHandler.get_user_name_from_token(token, dev)

    if model_folder_name == "undefined":
        model_folder_name = "Default"
    if not cluster:
        remotepath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
        try:
            output_files = os.listdir(remotepath)
            filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
            paths = [os.path.join(remotepath, basename) for basename in filtered_values]
            latest_file = max(paths, key=os.path.getctime)
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
        # log.info("remotepath: %s", remotepath)

        ssh, sftp = FileHandler.sftp_to_cluster(cluster)

        try:
            output_files = [x.filename for x in sorted(sftp.listdir_attr(remotepath), key=lambda f: f.st_mtime)]
            # log.info("output_files: %s", output_files)
            filtered_values = list(filter(lambda v: match(r"^.+\.log$", v), output_files))
            # log.info("filtered_values: %s", filtered_values)
            if len(filtered_values) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="LogFile can't be found in " + remotepath,
                )
            paths = [os.path.join(remotepath, basename) for basename in filtered_values]
            latest_file = paths[-1]
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
            logs = await log_reader(cluster, latest_file, debug)
            await websocket.send_text(logs)
    except WebSocketDisconnect:
        print("websocket disconnect")
    except Exception as e:
        print(e)
    finally:
        try:
            await websocket.close()
        except RuntimeError as e:
            pass
