# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import io
import json
import os
import time
from re import match

import numpy as np
import requests
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

# from ..models.PlateWithHole.plate_with_hole import PlateWithHole
# from ..models.PlateWithOpening.plate_with_opening import PlateWithOpening
# from ..models.RingOnRing.ring_on_ring import RingOnRing
# from ..models.Smetana.smetana import Smetana
from ..support.base_models import Block, Deviations, ModelData, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log
from ..support.model.point_cloud import build_point_cloud, valves_to_dict
from ..support.writer.model_writer import ModelWriter

# from ..models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
# from ..models.OwnModel.own_model import OwnModel


# from ..models.DCBmodel.dcb_model import DCBmodel
# from ..models.Dogbone.dogbone import Dogbone
# from ..models.ENFmodel.enf_model import ENFmodel
# from ..models.G1Cmodel.g1c_model import G1Cmodel


router = APIRouter(prefix="/generate", tags=["Generate Methods"])


@router.post("/model", operation_id="generate_model")
def generate_model(
    data: ModelData,
    valves: Valves,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):  # material: dict, Output: dict):
    """doc"""

    username = FileHandler.get_user_name(request, dev)

    max_nodes = FileHandler.get_max_nodes(username)

    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    json_file = os.path.join(localpath, model_name + ".json")
    ignore_mesh = False

    # if os.path.exists(json_file):
    #     with open(json_file, "r", encoding="UTF-8") as file:
    #         json_data = json.load(file)
    #         # print(data.model)
    #         if (
    #             data.model == json_data["model"]
    #             and data.boundaryConditions == json_data["boundaryConditions"]
    #         ):
    #             log.info("Model not changed")
    #             ignore_mesh = True

    with open(json_file, "w", encoding="UTF-8") as file:
        file.write(data.to_json())

    start_time = time.time()

    log.info("Create %s", model_name)

    if not data.model.ownModel:

        valves_dict = valves_to_dict(valves)
        try:
            dx_value, x_value, y_value, z_value, vol, k = build_point_cloud(model_name, data, valves_dict)
        except LookupError as e:
            log.error(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        if len(x_value) > max_nodes:
            log.error("The number of nodes (" + str(len(x_value)) + ") is larger than the allowed " + str(max_nodes))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The number of nodes (" + str(len(x_value)) + ") is larger than the allowed " + str(max_nodes),
            )

        # if data.model.rotatedAngles:
        #     angle_x = np.zeros(len(x_value))
        #     angle_y = np.zeros(len(x_value))
        #     angle_z = np.zeros(len(x_value))
        # check if vol is defined
        if vol is None:
            if data.model.twoDimensional:
                vol = np.full_like(
                    x_value,
                    dx_value[0] * dx_value[1],
                )
            else:
                vol = np.full_like(
                    x_value,
                    dx_value[0] * dx_value[1] * dx_value[2],
                )

    writer = ModelWriter(data, model_name, model_folder_name, username)

    # if data.model.rotatedAngles:
    #     model = np.transpose(
    #         np.vstack(
    #             [
    #                 x_value.ravel(),
    #                 y_value.ravel(),
    #                 z_value.ravel(),
    #                 k.ravel(),
    #                 vol.ravel(),
    #                 angle_x.ravel(),
    #                 angle_y.ravel(),
    #                 angle_z.ravel(),
    #             ]
    #         )
    #     )
    #     writer.write_mesh_with_angles(model, two_d)
    # else:
    if not data.model.ownModel:
        model = np.transpose(
            np.vstack(
                [
                    x_value.ravel(),
                    y_value.ravel(),
                    z_value.ravel(),
                    k.ravel(),
                    vol.ravel(),
                ]
            )
        )
        writer.write_mesh(model, data.model.twoDimensional)
        writer.write_node_sets(model)

        for i, block in enumerate(data.blocks):
            if isinstance(dx_value[0], float):
                block.horizon = 2.5 * max([dx_value[0], dx_value[1]])
            else:
                block.horizon = 2.5 * max([dx_value[i][0], dx_value[i][1]])
    else:
        k = [1e10]
    block_def = data.blocks

    # try:
    # deviations = {'sampleSize': 5, 'parameters': [{'id': "materials[0].youngsModulus", "mean": 0.1, "std": 10}]}
    writer.create_file(block_def, max(k), data.deviations)
    # except TypeError as exception:
    #     log.error(f"Failed to create file: {exception}")
    #     return str(exception)

    log.info("%s has been created in %.2f seconds", model_name, time.time() - start_time)


PREVIEW_MAX_DISCRETIZATION = 30
PREVIEW_MAX_POINTS = 5000


class PreviewResponse(BaseModel):
    x: list[float]
    y: list[float]
    z: list[float]
    block: list[int]
    bounds_min: list[float]
    bounds_max: list[float]


@router.post("/preview", operation_id="preview_model")
def preview_model(data: ModelData, valves: Valves, model_name: str = "Dogbone") -> PreviewResponse:
    """Coarse point cloud with block ids, drawn by the frontend as the model preview.

    Runs the generator exactly like /generate/model but with DISCRETIZATION capped and
    without writing anything, so it needs no user folder and works in trial mode.
    """
    valves_dict = valves_to_dict(valves)
    if "DISCRETIZATION" in valves_dict:
        valves_dict["DISCRETIZATION"] = min(valves_dict["DISCRETIZATION"], PREVIEW_MAX_DISCRETIZATION)

    try:
        _, x, y, z, _, k = build_point_cloud(model_name, data, valves_dict)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log.warning("Preview of %s failed: %s", model_name, e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e) or type(e).__name__)

    x, y, z, k = (np.asarray(a).ravel() for a in (x, y, z, k))
    if len(x) > PREVIEW_MAX_POINTS:
        # Even stride rather than random, so every block keeps proportional coverage.
        idx = np.linspace(0, len(x) - 1, PREVIEW_MAX_POINTS).astype(int)
        x, y, z, k = x[idx], y[idx], z[idx], k[idx]

    points = np.vstack([x, y, z]).astype(float)
    if points.size == 0:
        return PreviewResponse(x=[], y=[], z=[], block=[], bounds_min=[0, 0, 0], bounds_max=[0, 0, 0])
    rounded = [[float(f"{v:.4g}") for v in row] for row in points]
    return PreviewResponse(
        x=rounded[0],
        y=rounded[1],
        z=rounded[2],
        block=k.astype(int).tolist(),
        bounds_min=points.min(axis=1).tolist(),
        bounds_max=points.max(axis=1).tolist(),
    )


@router.get("/mesh", operation_id="generate_mesh")
def generate_mesh(
    model_name: str,
    param: str,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    # json=param,
    # print(param)

    request = requests.patch(
        "https://129.247.54.235:5000/1/PyCODAC/api/micofam/{zip}",
        verify=False,
    )
    try:
        with zipfile.ZipFile(io.BytesIO(request.content)) as zip_file:
            localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

            if not os.path.exists(localpath):
                os.makedirs(localpath)

            zip_file.extractall(localpath)

    except IOError:
        log.error("Micofam request failed")
        return "Micofam request failed"

    output_files = os.listdir(localpath)
    filtered_values = list(filter(lambda v: match(r"^.+\.inp$", v), output_files))
    os.rename(
        os.path.join(localpath, filtered_values[0]),
        os.path.join(localpath, model_name + ".inp"),
    )

    # return requests.patch('https://localhost:5000/1/PyCODAC/api/micofam/%7Bzip%7D', headers=headers, files=files)

    # file_path = './simulations/' + os.path.join(username, model_name) + '/'  + model_name + '.' + file_type
    # if not os.path.exists(file_path):
    #     return 'Inputfile can\'t be found'
    # try:
    #     return FileResponse(file_path)
    # except Exception:
    log.info("Mesh generated")
