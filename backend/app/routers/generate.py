# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import io
import json
import os
import time
from re import match

import requests
from fastapi import APIRouter, Request

from models.CompactTension.compact_tension import CompactTension
from models.DCBmodel.dcb_model import DCBmodel
from models.Dogbone.dogbone import Dogbone
from models.ENFmodel.enf_model import ENFmodel
from models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
from models.OwnModel.own_model import OwnModel
from models.PlateWithHole.plate_with_hole import PlateWithHole
from models.PlateWithOpening.plate_with_opening import PlateWithOpening
from models.Smetana.smetana import Smetana
from support.base_models import ModelData, ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/generate", tags=["Generate Methods"])


@router.post("/model")
def generate_model(
    model_data: ModelData,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):  # material: dict, Output: dict):
    """doc"""

    username = FileHandler.get_user_name(request, dev[0])

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
    if model_name in {"Dogbone", "Kalthoff-Winkler"}:
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

    if model_data.model.ownModel is False:
        if model_name == "ENFmodel":
            enf = ENFmodel(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = enf.create_model()

        elif model_name == "DCBmodel":
            dcb = DCBmodel(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = dcb.create_model()

        elif model_name == "Dogbone":
            dogbone = Dogbone(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = dogbone.create_model()

        elif model_name == "Kalthoff-Winkler":
            kalthoff = KalthoffWinkler(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = kalthoff.create_model()

        elif model_name == "PlateWithOpening":
            plate_with_opening = PlateWithOpening(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = plate_with_opening.create_model()

        elif model_name == "PlateWithHole":
            plate_with_hole = PlateWithHole(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = plate_with_hole.create_model()

        elif model_name == "CompactTension":
            compact_tension = CompactTension(
                model_data=model_data,
                model_folder_name=model_folder_name,
                username=username,
                max_nodes=max_nodes,
                ignore_mesh=ignore_mesh,
                dx_value=dx_value,
            )
            result = compact_tension.create_model()

        elif model_name == "Smetana":
            smetana = Smetana(
                model_folder_name=model_folder_name,
                mesh_res=model_data.model.discretization,
                xend=length,
                plyThickness=height,
                zend=width,
                dx_value=dx_value,
                damage=model_data.damages,
                contact=model_data.contact,
                compute=model_data.computes,
                output=model_data.outputs,
                solver=model_data.solver,
                model_data=model_data,
                username=username,
                ignore_mesh=ignore_mesh,
                amplitude_factor=model_data.model.amplitudeFactor,
                wavelength=model_data.model.wavelength,
                angle=model_data.model.angles,
                two_d=model_data.model.twoDimensional,
            )
            result = smetana.create_model()

        else:
            log.error("Model Name unknown")
            return "Model Name unknown"

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

    log.info("%s has been created in %.2f seconds", model_name, time.time() - start_time)

    if result != "Model created":
        return ResponseModel(data=False, message=result)

    return ResponseModel(
        data=True,
        message=f"{model_name} has been created in {time.time() - start_time} seconds.",
    )


@router.get("/mesh")
def generate_mesh(
    model_name: str,
    param: str,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    # json=param,
    # print(param)

    request = requests.patch(
        "https://129.247.54.235:5000/1/PyCODAC/api/micofam/{zip}",
        verify=False,
    )
    try:
        with zipfile.ZipFile(io.BytesIO(request.content)) as zip_file:
            localpath = "./Output/" + os.path.join(username, model_name, model_folder_name)

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

    # file_path = './Output/' + os.path.join(username, model_name) + '/'  + model_name + '.' + file_type
    # if not os.path.exists(file_path):
    #     return 'Inputfile can\'t be found'
    # try:
    #     return FileResponse(file_path)
    # except Exception:
    log.info("Mesh generated")
    return ResponseModel(data=True, message="Mesh generated")
