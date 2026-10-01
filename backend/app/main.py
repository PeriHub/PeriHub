# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import copy
import os
from contextlib import asynccontextmanager
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, HTTPBearer
from fastapi.staticfiles import StaticFiles

from .routers import admin as admin_router
from .routers import api_keys as api_keys_router
from .routers import auth as auth_router
from .routers import config as config_router
from .routers import delete, docs, energy, generate, jobs, library
from .routers import license as license_router
from .routers import model
from .routers import oauth as oauth_router
from .routers import projects as projects_router
from .routers import results
from .routers import teams as teams_router
from .routers import upload, usage
from .support.base_models import VersionData
from .support.file_handler import FileHandler
from .support.globals import (
    database_url,
    frontmatter_installation,
    guest_access,
    log,
)
from .support.model import loader
from .support.solver_backend import get_solver_backend

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
    {
        "name": "Auth Methods",
        "description": "Local email/password signup, login, and current-user info",
    },
    {
        "name": "Library Methods",
        "description": "Shared model configs and materials (create, list, update, delete, search)",
    },
    {
        "name": "Project Methods",
        "description": "Projects (workspaces) and teams - grouping and membership for shared resources",
    },
    {
        "name": "Config Methods",
        "description": "Public deployment config the frontend reads at startup (guest access, OAuth availability, etc.)",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown of the application."""
    # Startup
    if frontmatter_installation:
        for model in loader.list_models("own"):
            try:
                FileHandler.install_frontmatter_requirements(model.get("requirements", ""))
            except Exception as e:  # noqa: BLE001 - one bad requirement mustn't stop startup
                log.warning("Installing requirements of %s failed: %s", model["file"], e)

    if database_url:
        from sqlalchemy import text

        from .db.base import get_engine

        try:
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("Database connection OK")
        except Exception as exc:  # noqa: BLE001 - startup diagnostics only
            log.warning(
                "Could not connect to DATABASE_URL at startup (%s). Accounts and "
                "shared model configs/materials will be unavailable until this "
                "is reachable. Run `alembic upgrade head` if the schema hasn't "
                "been created yet.",
                exc,
            )

    sweeper = None
    if database_url:
        from .support import guest_sweeper

        sweeper = asyncio.create_task(guest_sweeper.run_forever())
    elif guest_access:
        log.warning("GUEST_ACCESS=True is ignored: guest accounts need DATABASE_URL.")

    yield
    # Shutdown
    if sweeper is not None:
        sweeper.cancel()


# Declared only so the OpenAPI spec says how to authenticate; resolve_user() does the actual check, and
# auto_error=False keeps public endpoints (login, /config/public, ...) public.
_api_key = APIKeyHeader(name="X-Api-Key", auto_error=False, description="Personal API key (user settings)")
_bearer = HTTPBearer(auto_error=False, description="Session token from POST /auth/login")

app = FastAPI(
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    version="4.0.0",
    dependencies=[Security(_api_key), Security(_bearer)],
)


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
app.include_router(jobs.router)
app.include_router(results.router)
app.include_router(delete.router)
app.include_router(docs.router)
app.include_router(energy.router)
app.include_router(usage.router)
app.include_router(license_router.router)
app.include_router(auth_router.router)
app.include_router(api_keys_router.router)
app.include_router(oauth_router.router)
app.include_router(library.router)
app.include_router(projects_router.router)
app.include_router(teams_router.router)
app.include_router(config_router.router)
app.include_router(admin_router.router)


@app.get("/health")
async def healthcheck():
    """Liveness probe."""
    return {"status": True}


# The operations a workflow agent needs; everything else (admin, teams, 3D-viewer data, ...) is left out of
# /openapi.agent.json so the agent doesn't have to search 60+ operations. A unit test checks these ids exist.
AGENT_OPERATIONS = {
    "get_models",
    "get_valves",
    "get_config",
    "get_analyses",
    "generate_model",
    "view_input_file",
    "run_model",
    "get_run",
    "get_run_log",
    "cancel_run",
    "list_all_runs",
    "get_run_summary",
    "run_analysis",
}

AGENT_WORKFLOW = """Run peridynamic simulations with PeriHub. Authenticate with a personal API key (`X-Api-Key`).

1. `get_models` -> pick a model; `get_valves` returns its parameters (`valves`).
2. `get_config` -> the model's default `ModelData`; edit it.
3. `generate_model` with `{"data": ModelData, "valves": valves}` -> writes the model folder (`GenerateResult`).
4. `run_model` with the same ModelData as body -> `run_id`.
5. Poll `get_run` until `status` is final (`done`, `failed`, `cancelled`). On `failed`, read
   `get_run_log` (`tail=200`), fix the config and go back to 3.
6. `get_run_summary` -> min/max of the results to judge the run; `run_analysis` renders a model analysis as PNG.
"""


@app.get("/openapi.agent.json", include_in_schema=False)
def agent_openapi() -> dict:
    """The workflow subset of /openapi.json for agents that only see a spec."""
    spec = copy.deepcopy(app.openapi())  # app.openapi() is cached; never edit it in place
    spec["paths"] = {
        path: kept
        for path, operations in spec["paths"].items()
        if (kept := {method: op for method, op in operations.items() if op.get("operationId") in AGENT_OPERATIONS})
    }
    spec["info"]["description"] = AGENT_WORKFLOW
    # Relative to where the spec was loaded from: /api/ behind nginx, / in dev.
    spec["servers"] = [{"url": "."}]
    return spec


@app.get("/version", operation_id="get_version")
async def get_app_latest_release_version() -> VersionData:
    """Running and latest released versions of PeriHub and PeriLab; "unknown" where PeriLab or GitHub can't be
    reached."""
    current = app.version
    latest = "unknown"
    perilab_current = "unknown"
    perilab_latest = "unknown"

    try:
        perilab_current = get_solver_backend().client().version()
    except HTTPException as e:
        log.debug("Could not reach PeriLab API for version: %s", e)

    try:
        r = requests.get("https://api.github.com/repos/PeriHub/PeriHub/tags", timeout=10)
        r.raise_for_status()
        latest = r.json()[0]["name"]

        r = requests.get(
            "https://api.github.com/repos/PeriHub/PeriLab.jl/releases/latest",
            timeout=10,
        )
        r.raise_for_status()
        perilab_latest = r.json()["tag_name"]
    except Exception as e:
        log.debug(e)

    return VersionData(
        current=current,
        latest=latest,
        perilab_current=perilab_current,
        perilab_latest=perilab_latest,
    )
