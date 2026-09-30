# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import ast
import json
import os
import shutil
from pathlib import Path
from typing import Literal, Optional

import numpy as np
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse
from slugify import slugify

from ..db import base
from ..support.base_models import AnalysisInfo, ModelData, PointData, Valves
from ..support.db_auth import resolve_user
from ..support.file_handler import FileHandler
from ..support.globals import log, max_nodes
from ..support.model import loader, mesh_readers
from ..support.model.yaml_model import ModelSpecError
from ..support.model.yaml_model import model_class as yaml_model_class
from ..support.rbac import require_role

router = APIRouter(tags=["Model Methods"])

OWN_MODELS = loader.MODEL_DIRS["own"]
ASSETS = loader.APP_DIR / "assets"


@router.get("/models", operation_id="get_models")
def get_models(own_only: bool = False, verify: bool = False, request: Request = "") -> list[dict]:
    """Built-in models, then own models (an own model named like a built-in one is shadowed
    by it everywhere, so it isn't listed twice).

    `own_only`: just the own models, shadowed ones included; broken or legacy-format ones
    carry an `error` message. `verify` (with `own_only`): only those the caller authored."""
    own = loader.list_models("own")
    if not own_only:
        model_list = loader.list_models("built_in")
        built_in = {model["file"] for model in model_list}
        return model_list + [model for model in own if model["file"] not in built_in]
    if verify:
        username = FileHandler.get_user_name(request)
        own = [model for model in own if username == "dev" or username in model["author"].replace(" ", "").split(",")]
    return own


@router.get("/models/{model_name}/params", operation_id="get_valves")
def get_valves(model_name: str) -> Valves:
    """The model's parameters as UI fields."""
    try:
        model_class = loader.load_model(model_name)
    except LookupError:
        return {"valves": []}
    return {"valves": [param.valve() for param in model_class.params()]}


@router.get("/models/{model_name}/analyses", operation_id="get_analyses")
def get_analyses(model_name: str) -> list[AnalysisInfo]:
    """The model's @analysis functions (result images) and their parameters; [] if none."""
    try:
        analyses = loader.load_analyses(model_name)
    except LookupError as e:
        log.warning(e)
        return []
    return [
        {
            "id": fn.perihub_analysis["id"],
            "label": fn.perihub_analysis["label"],
            "params": [param.valve() for param in fn.perihub_analysis["params"]],
        }
        for fn in analyses.values()
    ]


@router.get("/models/{model_name}/config", operation_id="get_config")
def get_config(model_name: str = "Dogbone") -> JSONResponse:
    """A model's default ModelData config (`<Name>.json`); a built-in model wins over an own model of the same name."""

    config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "models",
        model_name,
        model_name + ".json",
    )
    own_config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "own_models",
        model_name,
        model_name + ".json",
    )
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            data = json.load(file)
            return JSONResponse(content=data)
    if os.path.exists(own_config_path):
        with open(own_config_path, "r") as file:
            data = json.load(file)
            return JSONResponse(content=data)

    log.error("%s files can not be found", model_name)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=model_name + " files can not be found",
    )


def require_model_author(request: Request) -> None:
    """Own models run arbitrary Python on the server and default configs are shared by everyone, so only developers
    and admins may change them."""
    if base.SessionLocal is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Changing models requires an account.")
    with base.SessionLocal() as db:
        user = resolve_user(request, db).user
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    require_role(user, "developer")


@router.put("/models/{model_name}/config", operation_id="save_config", dependencies=[Depends(require_model_author)])
def save_config(model_name: str, config: ModelData, request: Request = ""):
    """Overwrite a model's default config with `config`, dropping empty top-level sections. Does nothing if the model
    has no config file."""
    username = FileHandler.get_user_name(request)

    config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "models",
        model_name,
        model_name + ".json",
    )
    own_config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "own_models",
        model_name,
        model_name + ".json",
    )
    if os.path.exists(config_path):
        file_path = config_path
    elif os.path.exists(own_config_path):
        file_path = own_config_path
    else:
        log.error("%s files can not be found", model_name)
        return
    # remove first layer object if value null
    config_dict = config.dict()
    remove_keys = []
    for key, value in config_dict.items():
        if not value:
            remove_keys.append(key)
    for k in remove_keys:
        del config_dict[k]
    # save config to file
    with open(file_path, "w") as file:
        file.write(json.dumps(config_dict))


@router.get("/workspaces/{model_name}/{model_folder_name}/download", operation_id="get_model")
def get_model(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):
    """Download a model folder (input deck, mesh, uploads) as a zip."""
    username = FileHandler.get_user_name(request)

    folder_path = os.path.join(FileHandler.get_local_user_path(username), model_name)
    zip_file = os.path.join(folder_path, model_name + "_" + model_folder_name)
    try:
        shutil.make_archive(zip_file, "zip", os.path.join(folder_path, model_folder_name))

        response = FileResponse(
            zip_file + ".zip",
            media_type="application/x-zip-compressed",
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=" + model_name + "_" + model_folder_name + ".zip"
        )
        # return StreamingResponse(iterfile(), media_type="application/x-zip-compressed")
        return response
    except shutil.Error:
        log.error("%s files can not be found", model_name)
        return model_name + " files can not be found"


@router.get("/workspaces/{model_name}/{model_folder_name}/points", operation_id="get_point_data")
def get_point_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    mesh_file: Optional[str] = None,
    two_d: Optional[bool] = True,
    request: Request = "",
) -> PointData:
    """Point cloud of a model for the 3D view: flat xyz coordinates plus block ids normalized to (0, 1].
    Read from the uploaded mesh `mesh_file` (text or Exodus) or else the generated `<model>.txt`; meshes above
    the node limit are thinned."""
    username = FileHandler.get_user_name(request)
    folder = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
    try:
        xyz, block = mesh_readers.read_points(os.path.join(folder, mesh_file or model_name + ".txt"), two_d)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{mesh_file or model_name} not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if len(xyz) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The mesh has no points")

    # Mean distance between consecutive points, as a sphere radius for the view.
    dx_value = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).mean()) if len(xyz) > 1 else 1.0
    if len(xyz) > max_nodes:
        reduce_factor = len(xyz) // max_nodes
        log.info(f"Number of nodes in file is too large, only every {reduce_factor}th node is read!")
        xyz, block = xyz[::reduce_factor], block[::reduce_factor]
    max_block_id = int(block.max())
    block_ids = np.full(len(block), 0.1) if max_block_id == 1 else block / max_block_id
    return PointData(points=xyz.ravel().tolist(), block_ids=block_ids.tolist(), dx_value=dx_value)


@router.get("/workspaces/{model_name}/{model_folder_name}/files/{filename}", operation_id="get_workspace_file")
def get_workspace_file(model_name: str, model_folder_name: str, filename: str, request: Request = ""):
    """A single file of a model folder, e.g. an uploaded G-code mesh for the browser preview."""
    username = FileHandler.get_user_name(request)
    folder = Path(FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)).resolve()
    path = (folder / filename).resolve()
    if path.parent != folder or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{filename} not found")
    return FileResponse(path)


@router.get("/workspaces/{model_name}/{model_folder_name}/input-deck", operation_id="view_input_file")
def view_input_file(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
) -> str:
    """The model folder's PeriLab input deck (`<model>.yaml`) as text; 400 if it hasn't been generated yet."""
    username = FileHandler.get_user_name(request)

    file_path = (
        FileHandler.get_local_model_folder_path(username, model_name, model_folder_name) + "/" + model_name + ".yaml"
    )
    log.info("Inputfile: %s", file_path)
    if not os.path.exists(file_path):
        log.error("Inputfile can't be found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inputfile can't be found",
        )
    try:
        with open(file_path, "r") as f:
            string = f.read()
        return string
    except IOError:
        log.error("Inputfile can't be found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inputfile can't be found",
        )


def _own_model_path(model_file: str, part: str) -> Path:
    """The editable file of an own model: its generator, or a YAML model's analysis.py."""
    folder = OWN_MODELS / model_file
    if not model_file or folder.resolve().parent != OWN_MODELS.resolve() or not folder.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Own model {model_file} not found")
    if part == "analysis":
        return folder / "analysis.py"
    for suffix in (".yaml", ".py"):
        if (folder / (model_file + suffix)).is_file():
            return folder / (model_file + suffix)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Own model {model_file} has no model file")


@router.post("/models", operation_id="add_model", dependencies=[Depends(require_model_author)])
def add_model(
    model_name: str, description: str, model_format: Literal["yaml", "python"] = "yaml", request: Request = ""
) -> str:
    """Create an own model from the YAML (default) or Python template; returns its folder name."""
    username = FileHandler.get_user_name(request)
    model_slug = slugify(model_name, separator="_")
    folder_path = OWN_MODELS / model_slug
    if folder_path.exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Model {model_slug} already exists")

    suffix = ".yaml" if model_format == "yaml" else ".py"
    template = (ASSETS / ("model_template" + suffix)).read_text(encoding="utf-8")
    for key, value in (("title", model_name), ("description", description), ("author", username)):
        template = template.replace("{" + key + "}", value.replace('"', "'"))

    folder_path.mkdir(parents=True)
    (folder_path / (model_slug + suffix)).write_text(template, encoding="utf-8")
    shutil.copy(ASSETS / "config_template.json", folder_path / (model_slug + ".json"))
    return model_slug


@router.get("/models/{model_name}/source", operation_id="get_own_model_file")
def get_own_model_file(model_name: str = "Dogbone", part: Literal["model", "analysis"] = "model") -> str:
    """Source of an own model (`part=analysis`: a YAML model's analysis.py, "" if it has none)."""
    path = _own_model_path(model_name, part)
    return path.read_text(encoding="utf-8") if path.is_file() else ""


@router.put("/models/{model_name}/source", operation_id="save_model_file", dependencies=[Depends(require_model_author)])
def save_model(
    model_name: str,
    source_code: str = Body(embed=True),
    part: Literal["model", "analysis"] = "model",
    request: Request = "",
):
    """Save an own model's source after a syntax check (YAML: full model validation)."""
    FileHandler.get_user_name(request)
    path = _own_model_path(model_name, part)
    try:
        if path.suffix == ".yaml":
            yaml_model_class(source_code, model_name)
        else:
            ast.parse(source_code)
    except SyntaxError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"line {e.lineno}: {e.msg}")
    except ModelSpecError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if part == "analysis" and not source_code.strip():
        path.unlink(missing_ok=True)
        return
    path.write_text(source_code, encoding="utf-8")


@router.delete("/models/{model_name}", operation_id="delete_model_file", dependencies=[Depends(require_model_author)])
def delete_model(model_name: str):
    """Delete an own model's folder (generator, default config, analysis.py)."""
    folder = OWN_MODELS / model_name
    if not model_name or folder.resolve().parent != OWN_MODELS.resolve():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Own model {model_name} not found")
    shutil.rmtree(folder, ignore_errors=True)
