# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import io
import json
import os
import time
from re import match

import requests
from fastapi import APIRouter, Request

from ..models.CompactTension.compact_tension import CompactTension

# from ..models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from ..models.OwnModel.own_model import OwnModel

# from ..models.PlateWithHole.plate_with_hole import PlateWithHole
# from ..models.PlateWithOpening.plate_with_opening import PlateWithOpening
# from ..models.RingOnRing.ring_on_ring import RingOnRing
# from ..models.Smetana.smetana import Smetana
from ..support.base_models import Block, ModelData, ResponseModel, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log

# from ..models.DCBmodel.dcb_model import DCBmodel
# from ..models.Dogbone.dogbone import Dogbone
# from ..models.ENFmodel.enf_model import ENFmodel
# from ..models.G1Cmodel.g1c_model import G1Cmodel


router = APIRouter(prefix="/generate", tags=["Generate Methods"])


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

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    json_file = os.path.join(localpath, model_name + ".json")
    ignore_mesh = False

    if os.path.exists(json_file):
        with open(json_file, "r", encoding="UTF-8") as file:
            json_data = json.load(file)
            # print(model_data.model)
            if (
                model_data.model == json_data["model"]
                and model_data.boundaryConditions == json_data["boundaryConditions"]
            ):
                log.info("Model not changed")
                ignore_mesh = True

    with open(json_file, "w", encoding="UTF-8") as file:
        file.write(model_data.to_json())

    # length = 152
    # length = 50
    # width = 10
    # height = 4.95
    # number_nodes = 12

    length = model_data.model.length
    cracklength = model_data.model.cracklength
    width = model_data.model.width
    height = model_data.model.height
    if model_name in {"Dogbone", "Kalthoff-Winkler", "RingOnRing"}:
        number_nodes = 2 * int(model_data.model.discretization / 2)
    else:
        number_nodes = 2 * int(model_data.model.discretization / 2) + 1
    if model_name in {"CompactTension"}:
        dx_value = [
            1.25 * length / number_nodes,
            1.25 * length / number_nodes,
            1.25 * length / number_nodes,
        ]
    elif model_name in {"Smetana"}:
        dx_value = [
            8 * height / number_nodes,
            8 * height / number_nodes,
            8 * height / number_nodes,
        ]
    else:
        dx_value = [
            height / number_nodes,
            height / number_nodes,
            height / number_nodes,
        ]

    start_time = time.time()

    log.info("Create %s", model_name)

    valves_dict = {valve["name"]: valve["value"] for valve in valves.model_dump()["valves"]}

    if model_data.model.ownModel is False:
        try:
            module = getattr(__import__("app.models." + model_name, fromlist=[model_name]), "main")
        except:
            try:
                module = getattr(__import__("app.own_models." + model_name, fromlist=[model_name]), "main")
            except:
                log.error("Model Name unknown")
                return "Model Name unknown"

        model = module(
            model_data=model_data,
            valves=valves_dict,
            model_folder_name=model_folder_name,
            username=username,
            max_nodes=max_nodes,
            ignore_mesh=ignore_mesh,
            dx_value=dx_value,
        )
        writer, block_len = model.create_model()

        if not model_data.blocks:
            block_dict = []
            mat_block = [model_data.materials[0].name] * block_len
            dam_block = [""] * block_len
            dam_block[0] = model_data.damages[0].name
            scal = 3.01
            for idx in range(0, block_len):
                block_def = Block(
                    id=1,
                    name="block_" + str(idx + 1),
                    material=mat_block[idx],
                    damageModel=dam_block[idx],
                    horizon=scal * max([dx_value[0], dx_value[1]]),
                    show=False,
                )
                block_dict.append(block_def)
            block_def = block_dict
        else:
            for _, block in enumerate(model_data.blocks):
                block.horizon = scal * max([dx_value[0], dx_value[1]])
            block_def = model_data.blocks

        try:
            writer.create_file(block_def)
        except TypeError as exception:
            return str(exception)

        # elif model_name == "Smetana":
        #     smetana = Smetana(
        #         model_folder_name=model_folder_name,
        #         mesh_res=model_data.model.discretization,
        #         xend=length,
        #         plyThickness=height,
        #         zend=width,
        #         dx_value=dx_value,
        #         model_data=model_data,
        #         username=username,
        #         ignore_mesh=ignore_mesh,
        #         amplitude_factor=model_data.model.amplitudeFactor,
        #         wavelength=model_data.model.wavelength,
        #         angle=model_data.model.angles,
        #         two_d=model_data.model.twoDimensional,
        #     )
        #     result = smetana.create_model()

    else:
        if model_data.model.translated:
            disc_type = "e"
        else:
            disc_type = "txt"

        own = OwnModel(
            model_data=model_data,
            filename=model_name,
            model_folder_name=model_folder_name,
            username=username,
            disc_type=disc_type,
            dx_value=dx_value,
        )
        result = own.create_model()

    if result != "Model created":
        log.warning(result)
        return ResponseModel(data=False, message=result)

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
            localpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)

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
