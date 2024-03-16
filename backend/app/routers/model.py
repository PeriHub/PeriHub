# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import csv
import os
import shutil
from re import findall

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

from support.base_models import ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/model", tags=["Model Methods"])


@router.get("/getMaxFeSize")
def get_max_fe_size(request: Request = ""):
    """doc"""

    username = FileHandler.get_user_name(request, dev)

    return FileHandler.get_max_fe_size(username)


@router.get("/getModel")
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


@router.get("/getPointData")
def get_point_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    own_model: bool = False,
    own_mesh: bool = False,
    mesh_file: str = "Dogbone.txt",
    two_d: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    point_string = ""
    block_id_string = ""
    if own_mesh:
        try:
            with open(
                "./simulations/"
                + os.path.join(username, model_name, model_folder_name)
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
                    point_string += coords[0][i] + "," + coords[1][i] + "," + coords[2][i] + ","
                    block_id_string += str(block_id[i] / num_of_blocks) + ","

            response = [
                point_string.rstrip(point_string[-1]),
                block_id_string.rstrip(block_id_string[-1]),
            ]
            return response
        except IOError:
            log.error("%s results can not be found", model_name)
            return model_name + " results can not be found"
    else:
        first_row = True
        max_block_id = 1
        try:
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
                for row in rows:
                    if not first_row:
                        str1 = "".join(row)
                        parts = str1.split()
                        if two_d:
                            block_id = int(parts[2])
                            point_string += parts[0] + "," + parts[1] + ",0.0,"
                        else:
                            block_id = int(parts[3])
                            point_string += parts[0] + "," + parts[1] + "," + parts[2] + ","
                        if block_id > max_block_id:
                            max_block_id = block_id
                    first_row = False
                first_row = True
                for row in rows:
                    if not first_row:
                        str1 = "".join(row)
                        parts = str1.split()
                        if two_d:
                            block_id = int(parts[2])
                        else:
                            block_id = int(parts[3])
                        if max_block_id == 1:
                            block_id_string += str(0.1) + ","
                        else:
                            block_id_string += str(block_id / max_block_id) + ","
                    first_row = False
            response = [
                point_string.rstrip(point_string[-1]),
                block_id_string.rstrip(block_id_string[-1]),
            ]
            return ResponseModel(data=response, message="Points received")
        except IOError:
            log.error("%s results can not be found", model_name)
            return model_name + " results can not be found"


@router.get("/viewInputFile")
def view_input_file(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    file_path = "./simulations/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + ".yaml"
    if not os.path.exists(file_path):
        log.error("Inputfile can't be found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inputfile can't be found",
        )
    try:
        with open(file_path, "r") as f:
            string = f.read()
        return ResponseModel(data=string, message="Input File received")
    except IOError:
        log.error("Inputfile can't be found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inputfile can't be found",
        )
