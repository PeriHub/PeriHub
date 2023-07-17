# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import datetime

import psutil
from typing import List

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Any
from pydantic import BaseModel

from support.file_handler import FileHandler
from support.globals import log

tags_metadata = [
    {"name": "Post Methods", "description": "Generate, translate or upload models"},
    {"name": "Put Methods", "description": "Run, cancel or write jobs"},
    {
        "name": "Get Methods",
        "description": "Get mesh files, input files or postprocessing data",
    },
    {"name": "Delete Methods", "description": "Delete user or model data"},
    {
        "name": "Documentation Methods",
        "description": "Retrieve markdown documentation or bibtex files",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

origins = [
    "http://localhost",
    "http://localhost:6010",
    "https://localhost:6010",
    "http://localhost:8080",
    "https://perihub.fa-services.intra.dlr.de",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()

dev = os.getenv("DEV")
if dev:
    print("--- Running in development mode ---")

PORTS = [6041, 6042, 6043, 6044, 6045]
used_ports = []
model_list = []
output_name_list = []
user_list = []
pid_list = []
time_list = []


class ResponseModel(BaseModel):
    data: Any
    code = 200
    message: str


class Launcher:
    """doc"""

    @app.post("/launchTrameInstance", tags=["Post Methods"])
    async def launch_trame_instance(
        model_name: str = "Dogbone",
        model_folder_name: str = "Default",
        output_name: str = "Output1",
        output_list: str = "[Displacement,Force]",
        dx_value: float = 0.1,
        num_of_blocks: int = 5,
        duration: int = 1000,
        request: Request = "",
    ):  # material: dict, Output: dict):
        """doc"""
        print(model_name)
        username = FileHandler.get_user_name(request, dev)

        newPort = 0

        for idx, _ in enumerate(model_list):
            if (
                model_list[idx] == model_name
                and output_name_list[idx] == output_name
                and user_list[idx] == username
            ):
                return used_ports[idx]

        for port in PORTS:
            if port not in used_ports:
                newPort = port
                break

        if newPort == 0:
            return "All ports are already used"

        command = (
            "./paraView/ParaView-5.11.1-osmesa-MPI-Linux-Python3.9-x86_64/bin/pvpython main.py "
            + username
            + " "
            + model_name
            + " "
            + model_folder_name
            + " "
            + output_name
            + " "
            + str(output_list).replace(" ", "").replace("[", "").replace("]", "")
            + " "
            + str(dx_value)
            + " "
            + str(num_of_blocks)
            + " --venv pvenv --port "
            + str(newPort)
            + " --host 0.0.0.0 -m paraview.apps.trame --trame-app main"
            # + " --ssl 'adhoc'"
        )

        try:
            p = subprocess.Popen(command, shell=True)
            used_ports.append(port)
            model_list.append(model_name)
            output_name_list.append(output_name)
            user_list.append(username)
            pid_list.append(p.pid)
            time_list.append(datetime.datetime.now() + datetime.timedelta(0, duration))
            print(used_ports)
            print(pid_list)
            print(time_list)
            # subprocess.call(command, shell=True)
        except subprocess.SubprocessError:
            return " results can not be found"
        return ResponseModel(
            data=newPort, message=f"Trame instance launched on port {newPort}!"
        )

    @app.post("/closeTrameInstance", tags=["Post Methods"])
    async def close_trame_instance(
        port: int, cron: bool, request: Request = ""
    ):  # material: dict, Output: dict):
        """doc"""

        if cron:
            for index, _ in enumerate(used_ports):
                if time_list[index] < datetime.datetime.now():
                    log.info("Close port " + str(used_ports[index]))
                    used_ports.pop(index)
                    model_list.pop(index)
                    output_name_list.pop(index)
                    user_list.pop(index)
                    time_list.pop(index)
                    try:
                        p = psutil.Process(pid_list[index])
                        p1 = psutil.Process(pid_list[index] + 1)
                        p2 = psutil.Process(pid_list[index] + 2)
                        p.terminate()
                        p1.terminate()
                        p2.terminate()
                    except psutil.NoSuchProcess:
                        pid_list.pop(index)
                        print("Process already terminated")
                    except FileNotFoundError:
                        pid_list.pop(index)
                        print("Process not found")
                    pid_list.pop(index)

        else:
            username = FileHandler.get_user_name(request, dev)

            print(used_ports)
            print(pid_list)
            index = used_ports.index(port)
            if user_list[index] == username:
                log.info("Close port " + str(used_ports[index]))
                used_ports.pop(index)
                model_list.pop(index)
                output_name_list.pop(index)
                user_list.pop(index)
                time_list.pop(index)
                try:
                    p = psutil.Process(pid_list[index])
                    p1 = psutil.Process(pid_list[index] + 1)
                    p2 = psutil.Process(pid_list[index] + 2)
                    p.terminate()
                    p1.terminate()
                    p2.terminate()
                except psutil.NoSuchProcess:
                    pid_list.pop(index)
                    log.warning("Process already terminated")
                except FileNotFoundError:
                    pid_list.pop(index)
                    log.warning("Process not found")
                pid_list.pop(index)

        print(used_ports)
        print(pid_list)

        return ResponseModel(
            data=True, message=f"Trame instance on port {port} closed!"
        )
