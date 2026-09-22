# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import requests
import toml
from fastapi import (
    FastAPI,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import (
    delete,
    docs,
    energy,
    generate,
    jobs,
)
from .routers import license as license_router
from .routers import (
    model,
    results,
    translate,
    upload,
    usage,
)
from .support.base_models import VersionData
from .support.file_handler import FileHandler
from .support.globals import dev, frontmatter_installation, log, trial, ws_log_wait_timeout_seconds

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
    {
        "name": "Usage Methods",
        "description": "Usage metering / job-submission analytics",
    },
    {
        "name": "License Methods",
        "description": "Plan & entitlement status from the license server",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown of the application."""
    # Startup
    if frontmatter_installation:
        file_path = str(Path(__file__).parent.resolve())
        try:
            for model in os.listdir(file_path + "/own_models"):
                if model.startswith("__"):
                    continue
                doc_string = FileHandler.get_docstring(os.path.join(file_path, "own_models", model, model + ".py"))
                if doc_string:
                    doc_dict = FileHandler.doc_to_dict(doc_string)
                    FileHandler.install_frontmatter_requirements(doc_dict.get("requirements", ""))
        except FileNotFoundError as e:
            print(e)
    yield
    # Shutdown


app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan, version="3.2.3")


banner = rf"""
██████╗ ███████╗██████╗ ██╗██╗  ██╗██╗   ██╗██████╗
██╔══██╗██╔════╝██╔══██╗██║██║  ██║██║   ██║██╔══██╗
██████╔╝█████╗  ██████╔╝██║███████║██║   ██║██████╔╝
██╔═══╝ ██╔══╝  ██╔══██╗██║██╔══██║██║   ██║██╔══██╗
██║     ███████╗██║  ██║██║██║  ██║╚██████╔╝██████╔╝
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝
v{app.version} - PeriHub
https://github.com/PeriHub/PeriHub.git
"""

print(banner)


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
app.include_router(usage.router)
app.include_router(license_router.router)

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


def _find_latest_log_file(cluster, user_name, model_name, model_folder_name, not_before):
    """Looks for the job's .log file once, without raising if it isn't there
    yet - the caller decides whether to keep polling. Returns (log_file_path
    or None, remotepath) so callers can report *where* they're looking.
    `not_before` filters out a log file left over from a previous run - see
    FileHandler.write_run_marker_local/_remote.
    """
    if not cluster:
        remotepath = FileHandler.get_local_model_folder_path(user_name, model_name, model_folder_name)
        return FileHandler.find_latest_log_file_local(remotepath, not_before=not_before), remotepath

    remotepath = FileHandler.get_remote_model_path(user_name, model_name, model_folder_name)
    try:
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
    except Exception as e:
        log.warning("Could not reach cluster while waiting for log file: %s", e)
        return None, remotepath
    try:
        return FileHandler.find_latest_log_file_remote(sftp, remotepath, not_before=not_before), remotepath
    finally:
        sftp.close()
        ssh.close()


def _get_run_marker_time(cluster, user_name, model_name, model_folder_name):
    """Reads the submission-time marker written by run_model, so the wait
    loop below only accepts a .log file created at or after this run
    started - otherwise an older log left in the same folder from a
    previous run would look like "the" log right up until this run's log
    file happens to overtake it. Returns None (meaning "don't filter") if
    no marker is found, e.g. a job submitted before this existed, or the
    cluster can't be reached right now.
    """
    if not cluster:
        remotepath = FileHandler.get_local_model_folder_path(user_name, model_name, model_folder_name)
        return FileHandler.get_run_marker_time_local(remotepath)

    remotepath = FileHandler.get_remote_model_path(user_name, model_name, model_folder_name)
    try:
        ssh, sftp = FileHandler.sftp_to_cluster(cluster)
    except Exception as e:
        log.warning("Could not reach cluster to read run marker: %s", e)
        return None
    try:
        return FileHandler.get_run_marker_time_remote(sftp, remotepath)
    finally:
        sftp.close()
        ssh.close()


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
    """Streams a running job's log file over the socket.

    Submitting a job and its .log file actually appearing on disk aren't the
    same instant - starting a container or landing on a cluster node takes a
    few seconds. Rather than requiring the file to already exist at connect
    time (and forcing the frontend to guess how long to wait beforehand),
    this endpoint accepts the connection immediately and polls for the file,
    keeping the client informed with small JSON status messages so the user
    sees *why* nothing has appeared yet instead of a blank log view.

    Message shapes sent to the client:
      {"status": "waiting",   "message": str, "elapsed": int}
      {"status": "connected", "message": str}
      {"status": "log",       "content": str}
      {"status": "error",     "message": str}
    """
    await websocket.accept()

    if model_folder_name == "undefined":
        model_folder_name = "Default"

    poll_interval = 1.0 if not cluster else 3.0
    start_time = asyncio.get_event_loop().time()
    latest_file = None
    # Anchors "the log file for *this* run" - see _get_run_marker_time. None
    # (no marker found) means don't filter, so an old-format/legacy folder
    # still behaves exactly as before.
    not_before = _get_run_marker_time(cluster, user_name, model_name, model_folder_name)

    try:
        while latest_file is None:
            latest_file, remotepath = _find_latest_log_file(
                cluster, user_name, model_name, model_folder_name, not_before
            )
            if latest_file is not None:
                break

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > ws_log_wait_timeout_seconds:
                log.error("LogFile can not be found in %s after %.0fs", remotepath, elapsed)
                await websocket.send_json(
                    {
                        "status": "error",
                        "message": (
                            f"No log file appeared in {remotepath} after {int(elapsed)}s. "
                            "The job may have failed to start - check that a solver slot "
                            "was available or that the cluster is reachable."
                        ),
                    }
                )
                return

            await websocket.send_json(
                {
                    "status": "waiting",
                    "message": "Job submitted - waiting for the simulation to start writing its log file...",
                    "elapsed": int(elapsed),
                }
            )
            await asyncio.sleep(poll_interval)

        await websocket.send_json({"status": "connected", "message": f"Streaming {os.path.basename(latest_file)}"})

        while True:
            await asyncio.sleep(1)
            logs = await log_reader(cluster, latest_file, debug)
            await websocket.send_json({"status": "log", "content": "".join(logs)})
    except WebSocketDisconnect:
        print("websocket disconnect")
    except Exception as e:
        print(e)
    finally:
        try:
            await websocket.close()
        except RuntimeError as e:
            pass


@app.get("/updates", operation_id="get_version")
async def get_app_latest_release_version() -> VersionData:
    current = app.version
    latest = "unknown"
    perilab_current = "unknown"
    perilab_latest = "unknown"

    container = FileHandler.get_perilab_container()
    exit_code, output = container.exec_run(["sh", "-c", "awk -F'\"' '/version/{print $2}' /PeriLab/Project.toml"])
    if exit_code != 0:
        print(f"❌ Error while reading Project.toml: {output.decode().strip()}")
    else:
        perilab_current = output.decode().strip()

    try:
        r = requests.get("https://api.github.com/repos/PeriHub/PeriHub/tags", timeout=10)
        r.raise_for_status()
        latest = r.json()[0]["name"]

        r = requests.get("https://api.github.com/repos/PeriHub/PeriLab.jl/releases/latest", timeout=10)
        r.raise_for_status()
        perilab_latest = r.json()["tag_name"]
    except Exception as e:
        log.debug(e)

    return VersionData(current=current, latest=latest, perilab_current=perilab_current, perilab_latest=perilab_latest)
