# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import ast
import csv
import json
import math
import os
import shutil
from pathlib import Path
from re import findall
from typing import Literal, Optional

import numpy as np
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse
from slugify import slugify

from ..support.base_models import AnalysisInfo, ModelData, PointData, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log, max_nodes
from ..support.model import loader
from ..support.model.yaml_model import ModelSpecError
from ..support.model.yaml_model import model_class as yaml_model_class

router = APIRouter(prefix="/model", tags=["Model Methods"])

OWN_MODELS = loader.MODEL_DIRS["own"]
ASSETS = loader.APP_DIR / "assets"


@router.get("/getModels", operation_id="get_models")
def get_models() -> list[dict]:
    """Built-in models, then own models (an own model named like a built-in one is shadowed
    by it everywhere, so it isn't listed twice)."""
    model_list = loader.list_models("built_in")
    built_in = {model["file"] for model in model_list}
    return model_list + [model for model in loader.list_models("own") if model["file"] not in built_in]


@router.get("/getOwnModels", operation_id="get_own_models")
def get_own_models(verify: bool = False, request: Request = "") -> list[dict]:
    """Own models; broken or legacy-format ones are included with an `error` message."""
    model_list = loader.list_models("own")
    if verify:
        username = FileHandler.get_user_name(request, dev)
        model_list = [
            model
            for model in model_list
            if username == "dev" or username in model["author"].replace(" ", "").split(",")
        ]
    return model_list


@router.get("/getValves", operation_id="get_valves")
def get_valves(model_name: str) -> Valves:
    """The model's parameters as UI fields."""
    try:
        model_class = loader.load_model(model_name)
    except LookupError:
        return {"valves": []}
    return {"valves": [param.valve() for param in model_class.params()]}


@router.get("/analyses", operation_id="get_analyses")
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


@router.get("/getConfig", operation_id="get_config")
def get_config(config_file: str = "Dogbone") -> JSONResponse:
    """doc"""

    config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "models",
        config_file,
        config_file + ".json",
    )
    own_config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "own_models",
        config_file,
        config_file + ".json",
    )
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            data = json.load(file)
            return JSONResponse(content=data)
    if os.path.exists(own_config_path):
        with open(own_config_path, "r") as file:
            data = json.load(file)
            return JSONResponse(content=data)

    log.error("%s files can not be found", config_file)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=config_file + " files can not be found",
    )


@router.post("/saveConfig", operation_id="save_config")
def save_config(config_file: str, config: ModelData, request: Request = ""):
    username = FileHandler.get_user_name(request, dev)

    config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "models",
        config_file,
        config_file + ".json",
    )
    own_config_path = os.path.join(
        str(Path(__file__).parent.parent.resolve()),
        "own_models",
        config_file,
        config_file + ".json",
    )
    if os.path.exists(config_path):
        file_path = config_path
    elif os.path.exists(own_config_path):
        file_path = own_config_path
    else:
        log.error("%s files can not be found", config_file)
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


@router.get("/getMaxFeSize", operation_id="get_max_fe_size")
def get_max_fe_size(request: Request = "") -> int:
    """doc"""

    username = FileHandler.get_user_name(request, dev)

    return FileHandler.get_max_fe_size(username)


@router.get("/getModel", operation_id="get_model")
def get_model(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

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


@router.get("/getPointData", operation_id="get_point_data")
def get_point_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    own_model: bool = False,
    own_mesh: Optional[bool] = False,
    mesh_file: Optional[str] = "Dogbone.txt",
    two_d: Optional[bool] = True,
    request: Request = "",
) -> PointData:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    points = []
    block_ids = []
    if own_mesh:
        try:
            with open(
                FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
                + "/"
                + model_name
                + ".g.ascii",
                "r",
                encoding="UTF-8",
            ) as file:
                model_data = file.read()
                num_of_blocks = findall(r"num_el_blk\s=\s\d*\s;", model_data)
                num_of_blocks = int(num_of_blocks[0][13:][:2])
                coords = findall(r"coord.\s=\s[-\d.,\se]{1,}", model_data)
                nodes = findall(r"node_ns[\d]*\s=\s[\d,\s]*", model_data)
                block_id = [1] * len(coords[0])
                for i in range(0, 3):
                    coords[i] = coords[i][8:].replace(" ", "").split(",")
                for i in range(0, num_of_blocks):
                    nodes[i] = nodes[i * 2][8:].replace(" ", "").split("=")[1].split(",")
                    for node in nodes[i]:
                        block_id[int(node) - 1] = i + 1
                for i in range(0, len(coords[0])):
                    # points += coords[0][i] + "," + coords[1][i] + "," + coords[2][i] + ","
                    points.append(coords[0][i])
                    points.append(coords[1][i])
                    points.append(coords[2][i])
                    # block_id_string += block_id[i] / num_of_blocks) + ","
                    block_ids.append(block_id[i] / num_of_blocks)
            response = PointData(points, block_ids)
            return response
        except IOError:
            log.error("%s results can not be found", model_name)
            return model_name + " results can not be found"
    else:
        max_block_id = 1
        # try:
        if own_model:
            mesh_path = "./simulations/" + os.path.join(username, model_name, model_folder_name) + "/" + mesh_file
        else:
            mesh_path = (
                "./simulations/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + ".txt"
            )

        with open(
            mesh_path,
            "r",
            encoding="UTF-8",
        ) as file:
            reader = csv.reader(file)
            rows = list(reader)
            reduce_factor = 1
            counter = 0
            if len(rows) > max_nodes:
                reduce_factor = int(len(rows) / max_nodes)
                log.info(f"Number of nodes in file is too large, only every {reduce_factor}th node is read!")
            for row in rows:
                str1 = "".join(row)
                if str1.startswith("#") or str1.startswith("header") or len(str1) == 0:
                    continue
                counter += 1
                if counter == reduce_factor:
                    counter = 0
                else:
                    continue
                parts = str1.split()
                if two_d:
                    try:
                        block_id = int(parts[2])
                    except ValueError:
                        log.error("Model don't support 2D model, switch two dimensional model off")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Model don't support 2D model, switch two dimensional model off",
                        )
                    # points += parts[0] + "," + parts[1] + ",0.0,"
                    points.append(parts[0])
                    points.append(parts[1])
                    points.append("0.0")
                else:
                    if len(parts) < 3:
                        log.error("Model don't support 3D model, switch to two dimensional model")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Model don't support 3D model, switch to two dimensional model",
                        )
                    try:
                        block_id = int(parts[3])
                    except ValueError:
                        log.error("Model don't support 3D model, switch to two dimensional model")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Model don't support 3D model, switch to two dimensional model",
                        )
                    # points += parts[0] + "," + parts[1] + "," + parts[2] + ","
                    points.append(parts[0])
                    points.append(parts[1])
                    points.append(parts[2])
                if block_id > max_block_id:
                    max_block_id = block_id
            dx = []
            x_previous = None
            y_previous = None
            z_previous = None
            counter = 0
            for row in rows:
                str1 = "".join(row)
                if str1.startswith("#") or str1.startswith("header") or len(str1) == 0:
                    continue
                parts = str1.split()
                if two_d:
                    block_id = int(parts[2])
                    x = float(parts[0])
                    y = float(parts[1])
                    if x_previous != None:
                        dx.append(math.hypot(x - x_previous, y - y_previous))
                    x_previous = x
                    y_previous = y
                else:
                    block_id = int(parts[3])
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                    if x_previous != None:
                        dx.append(math.hypot(x - x_previous, y - y_previous, z - z_previous))
                    x_previous = x
                    y_previous = y
                    z_previous = z
                counter += 1
                if counter == reduce_factor:
                    counter = 0
                else:
                    continue
                if max_block_id == 1:
                    # block_id_string += str(0.1) + ","
                    block_ids.append(0.1)
                else:
                    # block_id_string += block_id / max_block_id + ","
                    block_ids.append(block_id / max_block_id)
        dx_value = np.average(dx)
        response = PointData(points=points, block_ids=block_ids, dx_value=dx_value)
        return response
        # except IOError:
        #     log.error("%s results can not be found", model_name)
        #     return model_name + " results can not be found"


@router.get("/viewInputFile", operation_id="view_input_file")
def view_input_file(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
) -> str:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

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


@router.post("/add", operation_id="add_model")
def add_model(
    model_name: str, description: str, model_format: Literal["yaml", "python"] = "yaml", request: Request = ""
) -> str:
    """Create an own model from the YAML (default) or Python template; returns its folder name."""
    username = FileHandler.get_user_name(request, dev)
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


@router.get("/getOwnModelFile", operation_id="get_own_model_file")
def get_own_model_file(model_file: str = "Dogbone", part: Literal["model", "analysis"] = "model") -> str:
    """Source of an own model (`part=analysis`: a YAML model's analysis.py, "" if it has none)."""
    path = _own_model_path(model_file, part)
    return path.read_text(encoding="utf-8") if path.is_file() else ""


@router.post("/save", operation_id="save_model_file")
def save_model(
    model_file: str,
    source_code: str = Body(embed=True),
    part: Literal["model", "analysis"] = "model",
    request: Request = "",
):
    """Save an own model's source after a syntax check (YAML: full model validation)."""
    FileHandler.get_user_name(request, dev)
    path = _own_model_path(model_file, part)
    try:
        if path.suffix == ".yaml":
            yaml_model_class(source_code, model_file)
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


@router.delete("/delete", operation_id="delete_model_file")
def delete_model(model_name: str):
    folder = OWN_MODELS / model_name
    if not model_name or folder.resolve().parent != OWN_MODELS.resolve():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Own model {model_name} not found")
    shutil.rmtree(folder, ignore_errors=True)
