# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import ast
import csv
import importlib.machinery
import importlib.util
import json
import math
import os
import shutil
from pathlib import Path
from re import findall
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse
from slugify import slugify

from ..support.base_models import ModelData, PointData, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log, max_nodes

router = APIRouter(prefix="/model", tags=["Model Methods"])


@router.get("/getModels", operation_id="get_models")
def get_models() -> list[dict]:
    """doc"""

    model_list = []
    file_path = str(Path(__file__).parent.parent.resolve())
    # print(file_path)
    for model in os.listdir(os.path.join(file_path, "models")):
        if model.startswith("__"):
            continue
        doc_string = FileHandler.get_docstring(os.path.join(file_path, "models", model, model + ".py"))
        if doc_string:
            doc_dict = FileHandler.doc_to_dict(doc_string)
            doc_dict["file"] = os.path.join(model)
            # doc_dict["config"] = os.path.join(model, model + ".json")
            # if doc_dict["input"] != input_type and input_type != "Any":
            #     continue
            # if own_models and username not in doc_dict["author"].replace(" ", "").split(","):
            #     continue
            model_list.append(doc_dict)

    model_list += get_own_models()

    return model_list


@router.get("/getOwnModels", operation_id="get_own_models")
def get_own_models(verify: bool = False, request: Request = "") -> list[str]:
    """doc"""

    model_list = []
    file_path = str(Path(__file__).parent.parent.resolve())
    file_path = os.path.join(file_path, "own_models")
    if not os.path.exists(file_path):
        return model_list
    # print(file_path)
    for model in os.listdir(file_path):
        if model.startswith("__"):
            continue
        doc_string = FileHandler.get_docstring(os.path.join(file_path, model, model + ".py"))
        if doc_string:
            doc_dict = FileHandler.doc_to_dict(doc_string)
            doc_dict["file"] = os.path.join(model)
            # doc_dict["config"] = os.path.join(model, model + ".json")
            # if doc_dict["input"] != input_type and input_type != "Any":
            #     continue
            if verify:
                username = FileHandler.get_user_name(request, dev)
                if username not in doc_dict["author"].replace(" ", "").split(",") and username != "dev":
                    continue
            model_list.append(doc_dict)

    return model_list


@router.get("/getValves", operation_id="get_valves")
def get_valves(model_name: str, source: bool = False) -> Valves:
    """doc"""
    parent_path = str(Path(__file__).parent.parent.name)

    # if source:
    #     file_path = os.path.join(str(Path(__file__).parent.parent.resolve()), "own_models", model_name + ".py")
    #     print(file_path)
    #     return Path(file_path).read_text()
    print(parent_path + ".models." + model_name + "." + model_name)
    try:
        module = importlib.import_module(parent_path + ".models." + model_name + "." + model_name, package=".")
    except:
        try:
            module = importlib.import_module(parent_path + ".own_models." + model_name + "." + model_name, package=".")
        except:
            return {"valves": []}
    if not hasattr(module, "Valves"):
        return {"valves": []}
    my_class = getattr(module, "Valves")
    my_instance = my_class()

    fields = my_instance.__fields__
    response = {"valves": []}
    for key in fields:
        type = "text"
        if fields[key].annotation.__name__ == "bool":
            type = "checkbox"
        elif fields[key].annotation.__name__ == "Any":
            type = "data"
        elif fields[key].annotation.__name__ in ["float", "int"]:
            type = "number"
        elif fields[key].annotation.__name__ == "str" and fields[key].examples:
            type = "select"
        response["valves"].append(
            {
                "name": key,
                "type": type,
                "value": fields[key].default,
                "label": fields[key].title,
                "description": fields[key].description,
                "options": fields[key].examples,
                "depends": fields[key].alias,
            }
        )
    return response


@router.get("/getConfig", operation_id="get_config")
def get_config(config_file: str = "Dogbone") -> ModelData:
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
            return json.load(file)
    if os.path.exists(own_config_path):
        with open(own_config_path, "r") as file:
            return json.load(file)

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

    with open(file_path, "w") as file:
        file.write(config.to_json())


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
                    points.append(str(coords[0][i]))
                    points.append(str(coords[1][i]))
                    points.append(str(coords[2][i]))
                    # block_id_string += str(block_id[i] / num_of_blocks) + ","
                    block_ids.append(str(block_id[i] / num_of_blocks))
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
                    points.append(str(parts[0]))
                    points.append(str(parts[1]))
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
                    points.append(str(parts[0]))
                    points.append(str(parts[1]))
                    points.append(str(parts[2]))
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
                    block_ids.append(str(0.1))
                else:
                    # block_id_string += str(block_id / max_block_id) + ","
                    block_ids.append(str(block_id / max_block_id))
        dx_value = np.average(dx)
        response = PointData(points, block_ids, dx_value)
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


@router.post("/add", operation_id="add_model")
def add_model(model_name: str, description: str, request: Request = "") -> str:
    """doc"""

    username = FileHandler.get_user_name(request, dev)

    model_slug = slugify(model_name, separator="_")

    folder_path = os.path.join(str(Path(__file__).parent.parent.resolve()), "own_models", model_slug)
    file_path = os.path.join(folder_path, model_slug + ".py")
    config_file_path = os.path.join(folder_path, model_slug + ".json")
    print(file_path)

    source_code = f'''
"""
| title: {model_name}
| description: {description}
| author: {username}
| requirements:
| version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ..support.model.geometry import Geometry

class Valves(BaseModel):
    DISCRETIZATION: float = Field(
        default=21,
        title="Discretization",
        description="Discretization",
    )
    LENGTH: float = Field(
        default=110,
        title="Length",
        description="Length",
    )
    HEIGHT: float = Field(
        default=3,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=25,
        title="Width",
        description="Width",
    )

class main:
    def __init__(
        self,
        valves,
    ):
        self.xbegin = 0
        self.xend = valves["LENGTH"]
        self.ybegin = 0
        self.yend = valves["HEIGHT"]
        self.discretization = valves["DISCRETIZATION"]
        self.two_d = model_data.model.twoDimensional

        if self.two_d:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

    def get_discretization(self):
        number_nodes = 2 * int(self.discretization / 2) + 1
        dx_value = [
            self.yend / number_nodes,
            self.yend / number_nodes,
            self.yend / number_nodes,
        ]
        self.dx_value = dx_value
        return dx_value

    def create_geometry(self):
        """doc"""

        geo = Geometry()

        x_value, y_value, z_value = geo.create_rectangle(
            coor=[
                self.xbegin,
                self.xend,
                self.ybegin,
                self.yend,
                self.zbegin,
                self.zend,
            ],
            dx_value=self.dx_value,
        )

        return (
            x_value,
            y_value,
            z_value,
            None
        )

    def edit_model_data(self, model_data):
        return model_data

    def crate_block_definition(self, x_value, y_value, z_value, k):
        """doc"""
        k = np.where(
            y_value <= self.yend / 2,
            2,
            k,
        )
        return k'''
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(file_path, "w") as file:
        file.write(source_code)

    shutil.copy(
        os.path.join(str(Path(__file__).parent.parent.resolve()), "assets", "config_template.json"), config_file_path
    )

    return model_slug


@router.get("/getOwnModelFile", operation_id="get_own_model_file")
def get_own_model_file(model_file: str = "Dogbone") -> str:
    """doc"""

    folder_path = str(Path(__file__).parent.parent.resolve())

    file_path = os.path.join(folder_path, "own_models", model_file, model_file + ".py")

    return Path(file_path).read_text()


@router.post("/save", operation_id="save_model_file")
def save_model(model_file: str, source_code: str, request: Request = ""):
    username = FileHandler.get_user_name(request, dev)

    file_path = os.path.join(str(Path(__file__).parent.parent.resolve()), "own_models", model_file, model_file + ".py")

    try:
        ast.parse(source_code)
    except SyntaxError as e:
        print(e)
        raise HTTPException(status_code=400, detail=e.msg)
    with open(file_path, "w") as file:
        file.write(source_code)


@router.delete("/delete", operation_id="delete_model_file")
def delete_model(model_name: str):
    file_path = os.path.join(str(Path(__file__).parent.parent.resolve()), "own_models", model_name)
    shutil.rmtree(file_path, ignore_errors=True)
