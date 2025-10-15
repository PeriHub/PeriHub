# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import importlib
import io
import json
import os
import sys
import time
from re import match

import numpy as np
import requests
from fastapi import APIRouter, HTTPException, Request, status

# from ..models.PlateWithHole.plate_with_hole import PlateWithHole
# from ..models.PlateWithOpening.plate_with_opening import PlateWithOpening
# from ..models.RingOnRing.ring_on_ring import RingOnRing
# from ..models.Smetana.smetana import Smetana
from ..support.base_models import Block, ModelData, ResponseModel, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log
from ..support.writer.model_writer import ModelWriter

# from ..models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
# from ..models.OwnModel.own_model import OwnModel


# from ..models.DCBmodel.dcb_model import DCBmodel
# from ..models.Dogbone.dogbone import Dogbone
# from ..models.ENFmodel.enf_model import ENFmodel
# from ..models.G1Cmodel.g1c_model import G1Cmodel


router = APIRouter(prefix="/generate", tags=["Generate Methods"])


def load_or_reload_main(model_name: str):
    """
    Dynamically import/reload `app.own_models.<model_name>.<model_name>`
    and return the `main` attribute from that module.
    """
    # Build the fully‑qualified module path
    module_name = f"app.own_models.{model_name}.{model_name}"

    # If the module is already loaded, reload it; otherwise, import it.
    if module_name in sys.modules:
        mod = importlib.reload(sys.modules[module_name])
    else:
        mod = importlib.import_module(module_name)

    # Pull the attribute you care about.
    return getattr(mod, "main")


@router.post("/model", operation_id="generate_model")
def generate_model(
    model_data: ModelData,
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
    #         # print(model_data.model)
    #         if (
    #             model_data.model == json_data["model"]
    #             and model_data.boundaryConditions == json_data["boundaryConditions"]
    #         ):
    #             log.info("Model not changed")
    #             ignore_mesh = True

    with open(json_file, "w", encoding="UTF-8") as file:
        file.write(model_data.to_json())

    start_time = time.time()

    log.info("Create %s", model_name)

    if not model_data.model.ownModel:

        valves_dict = {valve["name"]: valve["value"] for valve in valves.model_dump()["valves"]}

        try:
            module = getattr(
                __import__("app.models." + model_name + "." + model_name, fromlist=[model_name]),
                "main",
            )
        except:
            try:
                module = load_or_reload_main(model_name)
            except:
                log.error("Model Name unknown")
                return "Model Name unknown"

        model = module(valves_dict, model_data)

        dx_value = model.get_discretization()

        x_value, y_value, z_value, vol = model.create_geometry()

        try:
            model.edit_model_data(model_data)
        except:
            pass

        k = np.ones(len(x_value))

        k = model.crate_block_definition(x_value, y_value, z_value, k)
        if len(x_value) > max_nodes:
            log.error("The number of nodes (" + str(len(x_value)) + ") is larger than the allowed " + str(max_nodes))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The number of nodes (" + str(len(x_value)) + ") is larger than the allowed " + str(max_nodes),
            )

        # if model_data.model.rotatedAngles:
        #     angle_x = np.zeros(len(x_value))
        #     angle_y = np.zeros(len(x_value))
        #     angle_z = np.zeros(len(x_value))
        # check if vol is defined
        if vol is None:
            if model_data.model.twoDimensional:
                vol = np.full_like(
                    x_value,
                    dx_value[0] * dx_value[1],
                )
            else:
                vol = np.full_like(
                    x_value,
                    dx_value[0] * dx_value[1] * dx_value[2],
                )

    writer = ModelWriter(model_data, model_name, model_folder_name, username)

    # if model_data.model.rotatedAngles:
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
    if not model_data.model.ownModel:
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
        writer.write_mesh(model, model_data.model.twoDimensional)
        writer.write_node_sets(model)

        for i, block in enumerate(model_data.blocks):
            if isinstance(dx_value[0], float):
                block.horizon = 2.5 * max([dx_value[0], dx_value[1]])
            else:
                block.horizon = 2.5 * max([dx_value[i][0], dx_value[i][1]])
    else:
        k = [1e10]
    block_def = model_data.blocks

    try:
        writer.create_file(block_def, max(k))
    except TypeError as exception:
        log.error(f"Failed to create file: {exception}")
        return str(exception)

    log.info("%s has been created in %.2f seconds", model_name, time.time() - start_time)

    return ResponseModel(
        data=True,
        message=f"{model_name} has been created in {time.time() - start_time} seconds.",
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
    return ResponseModel(data=True, message="Mesh generated")
