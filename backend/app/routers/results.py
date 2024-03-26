# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import csv
import os
import shutil
from typing import Optional

import numpy as np
from exodusreader import exodusreader
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse

from support.base_models import ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log
from support.results.analysis import Analysis
from support.results.crack_analysis import CrackAnalysis

router = APIRouter(prefix="/results", tags=["Results Methods"])


@router.get("/getFractureAnalysis")
def get_fracture_analysis(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    length: float = 35,
    height: float = 10,
    crack_length: float = 17.5,
    young_modulus: float = 5000,
    poissions_ratio: float = 0.33,
    yield_stress: float = 74,
    cluster: bool = False,
    tasks: int = 32,
    output: str = "Output1",
    step: int = -1,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    file_name, filepath = CrackAnalysis.write_nodemap(file, step)

    filepath = CrackAnalysis.fracture_analysis(
        model_name,
        length,
        height,
        crack_length,
        young_modulus,
        poissions_ratio,
        yield_stress,
        file_name,
        filepath,
    )

    try:
        return FileResponse(filepath)
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


@router.get("/getEnfAnalysis")
def get_enf_analysis(
    model_name: str = "ENFmodel",
    model_folder_name: str = "Default",
    length: float = 15.0,
    width: float = 1.0,
    crack_length: float = 6.0,
    cluster: bool = False,
    tasks: int = 32,
    output: str = "Output1",
    step: int = -1,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    g2c = CrackAnalysis.get_g2c(file, length, width, crack_length, step)

    try:
        return g2c
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


@router.get("/getPlot")
def get_plot(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    output: str = "Output1",
    tasks: int = 32,
    # x_variable: str = "Time",
    # x_axis: str = "X",
    # x_absolute: bool = True,
    # y_variable: str = "External_Displacement",
    # y_axis: str = "X",
    # y_absolute: bool = True,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".csv")

    # x_data = Analysis.get_global_data(file, x_variable, x_axis, x_absolute)
    # y_data = Analysis.get_global_data(file, y_variable, y_axis, y_absolute)

    data = {}
    first_row = True
    # try:
    with open(file, "r", encoding="UTF-8") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if first_row:
                # Extract column names from the first row
                column_names = row
                for column_name in column_names:
                    data[column_name] = []

                first_row = False
            else:
                # Populate data dictionary with values
                for i, value in enumerate(row):
                    data[column_names[i]].append(value)

    return ResponseModel(data=data, message="Plot received")
    # except IOError:
    #     log.error("%s results can not be found on %s", model_name, cluster)
    #     return ResponseModel(data=data, message=model_name + " results can not be found on " + cluster)


@router.get("/getResults")
def get_results(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    tasks: int = 32,
    cluster: bool = False,
    all_data: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, all_data, tasks, output
    ):
        raise HTTPException(
            status_code=404,
            detail=model_name + " results can not be found on " + cluster,
        )

    # resultpath = './simulations/' + os.path.join(username, model_name)
    userpath = "./simulations/" + username
    folder_path = os.path.join(userpath, model_name)
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
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


@router.get("/getPointData")
def get_point_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    tasks: int = 32,
    cluster: bool = False,
    axis: str = "Magnitude",
    step: int = 78,
    displ_factor: float = 100,
    variable: str = "Displacements",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./simulations/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    number_of_steps = exodusreader.get_number_of_steps(file) - 3
    try:
        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

    except IndexError:
        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, number_of_steps)
    use_cell_data = False

    variable_list = list(point_data.keys())
    variable_list = list(set(item.rstrip("xyz") for item in variable_list))

    np_points_all_z = None
    use_multi_data = False

    if variable in [
        "Displacements",
        "Forces",
        "Partial_StressX",
        "Partial_StressY",
        "Partial_StressZ",
    ]:
        use_multi_data = True
    axis_id = 0

    if axis == "X":
        axis_id = 0
        if use_multi_data:
            variable = variable + "x"
    elif axis == "Y":
        axis_id = 1
        if use_multi_data:
            variable = variable + "y"
    elif axis == "Z":
        axis_id = 2
        if use_multi_data:
            variable = variable + "z"
    elif axis == "Magnitude":
        axis_id = 0

    if use_cell_data:
        np_points_all_x = np.array([])
        np_points_all_y = np.array([])
        np_points_all_z = np.array([])

        cell_value = np.array([])

        for block_id in range(0, len(block_data)):
            block_ids = block_data[block_id][:, 0]

            block_points = points[block_ids]

            np_first_points_x = np.array(block_points[:, 0])
            np_first_points_y = np.array(block_points[:, 1])
            np_first_points_z = np.array(block_points[:, 2])

            if "Displacements" in point_data:
                np_displacement_x = np.array(point_data["Displacements"][block_ids, 0])
                np_displacement_y = np.array(point_data["Displacements"][block_ids, 1])
                np_displacement_z = np.array(point_data["Displacements"][block_ids, 2])

                np_points_x = np.add(
                    np_first_points_x,
                    np.multiply(np_displacement_x, displ_factor),
                )
                np_points_y = np.add(
                    np_first_points_y,
                    np.multiply(np_displacement_y, displ_factor),
                )
                np_points_z = np.add(
                    np_first_points_z,
                    np.multiply(np_displacement_z, displ_factor),
                )
            else:
                np_points_x = np_first_points_x
                np_points_y = np_first_points_y
                np_points_z = np_first_points_z

            np_points_all_x = np.concatenate([np_points_all_x, np_points_x])
            np_points_all_y = np.concatenate([np_points_all_y, np_points_y])
            np_points_all_z = np.concatenate([np_points_all_z, np_points_z])

            if variable == "Block":
                cell_value = np.concatenate(
                    [
                        cell_value,
                        np.full_like(np_points_x, block_id),
                    ]
                )
            else:
                if block_id in cell_data[variable][0] and max(cell_data[variable][0][block_id]) > 0:
                    cell_value = np.concatenate(
                        [
                            cell_value,
                            cell_data[variable][0][block_id],
                        ]
                    )
                else:
                    cell_value = np.concatenate([cell_value, np.full_like(np_points_x, 0)])

    else:
        np_first_points_x = np.array(points[:, 0])
        np_first_points_y = np.array(points[:, 1])
        np_first_points_z = np.array(points[:, 2])

        try:
            np_displacement_x = np.array(point_data["Displacementsx"])
            np_displacement_y = np.array(point_data["Displacementsy"])
            try:
                np_displacement_z = np.array(point_data["Displacementsz"])
                np_points_all_z = np.add(
                    np_first_points_z,
                    np.multiply(np_displacement_z, displ_factor),
                )
            except:
                pass

            np_points_all_x = np.add(
                np_first_points_x,
                np.multiply(np_displacement_x, displ_factor),
            )
            np_points_all_y = np.add(
                np_first_points_y,
                np.multiply(np_displacement_y, displ_factor),
            )

        except Exception:
            print("No Displacements")
            np_points_all_x = np_first_points_x
            np_points_all_y = np_first_points_y
            np_points_all_z = np_first_points_z

        cell_value = []
        if axis == "Magnitude" and use_multi_data:
            cell_value_x = point_data[variable + "x"]
            cell_value_y = point_data[variable + "y"]
            cell_value = np.sqrt(cell_value_x**2 + cell_value_y**2)
        else:
            # cell_value = point_data[variable][:, axis_id]
            cell_value = point_data[variable]
    if np_points_all_z is None:
        np_points_all_z = np.zeros_like(np_points_all_x)

    min_cell_value = np.min(cell_value)
    max_cell_value = np.max(cell_value)
    if max_cell_value == min_cell_value:
        normalized_cell_value = np.zeros_like(cell_value)
    else:
        normalized_cell_value = (cell_value - min_cell_value) / (max_cell_value - min_cell_value)
    print(time)
    data = {
        "nodes": np.ravel([np_points_all_x, np_points_all_y, np_points_all_z], order="F").tolist(),
        "value": normalized_cell_value.tolist(),
        "variables": variable_list,
        "number_of_steps": number_of_steps,
        "min_value": min_cell_value,
        "max_value": max_cell_value,
        "time": np.format_float_scientific(time, 2),
    }

    return JSONResponse(content=data)
