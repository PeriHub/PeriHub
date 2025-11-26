# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import csv
import importlib
import json
import os
import shutil
import sys
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from exodusreader import exodusreader
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse

from ..support.base_models import ModelData, PointDataResults, Valves
from ..support.file_handler import FileHandler
from ..support.globals import dev, log, max_nodes
from ..support.results.analysis import Analysis
from ..support.results.crack_analysis import CrackAnalysis

router = APIRouter(prefix="/results", tags=["Results Methods"])


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


@router.post(
    "/getOwnAnalysis",
    operation_id="get_own_analysis",
    response_class=FileResponse,
    responses={
        200: {
            "description": "The image.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        }
    },
)
def get_own_analysis(
    data: ModelData,
    valves: Valves,
    model_name: str = "ENFmodel",
    output: str = "Output1",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    model_folder_name = data.model.modelFolderName
    cluster = data.job.cluster
    tasks = data.job.tasks

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

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

    model = module(valves_dict, data)
    return model.analysis(model_name, resultpath, output)


@router.get(
    "/getFractureAnalysis",
    operation_id="get_fracture_analysis",
    response_class=FileResponse,
    responses={
        200: {
            "description": "The image.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        }
    },
)
def get_fracture_analysis(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    height: float = 10,
    crack_length: float = 17.5,
    young_modulus: float = 5000,
    poissions_ratio: float = 0.33,
    yield_stress: float = 74,
    cluster: bool = False,
    tasks: int = 1,
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

    resultpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    file_name, filepath = CrackAnalysis.write_nodemap(file, step)

    crack_coordinate = CrackAnalysis.get_crack_end(file, step)

    filepath = CrackAnalysis.fracture_analysis(
        model_name,
        height,
        crack_coordinate,
        young_modulus,
        poissions_ratio,
        yield_stress,
        file_name,
        filepath,
    )

    return FileResponse(filepath, media_type="image/png")


@router.get("/getEnergyReleasePlot", operation_id="get_energy_release_plot")
def get_energy_release_plot(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    output_exodus: str = "Output1",
    output_csv: str = "Output2",
    tasks: int = 1,
    force_output_name: str = "External_Forcey",
    displacement_output_name: str = "External_Displacementy",
    step: int = -1,
    thickness: float = None,
    # crack_start: float = 56.25,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output_exodus
    ):
        raise IOError  # NotFoundException(name=model_name)
    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output_csv
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output_csv + ".csv")
    result_file = os.path.join(resultpath, model_name + "_" + output_csv + ".png")

    if not os.path.exists(file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=model_name + "_" + output_csv + ".csv can not be found"
        )

    df = pd.read_csv(file)

    file = os.path.join(resultpath, model_name + "_" + output_exodus + ".e")
    (crack_length, crack_width, time) = CrackAnalysis.get_crack_length(file, step)

    x = df[displacement_output_name]
    y1 = df[force_output_name]

    time_array = df["Time"]
    index = np.argmin(np.abs(time_array - time))
    y2 = np.linspace(0, y1[index], index)

    plt.clf()
    plt.plot(x, df[force_output_name], label="Original data")

    x = x[:index]
    y1 = y1[:index]

    plt.plot(x, y2, "r", label="Linear equation (y=x+2)")
    plt.fill_between(x, y1, y2, alpha=0.3, label="Area between lines")

    z = np.array(y1 - y2)
    dx = x[2] - x[1]
    areas_pos = abs(z[:-1] + z[1:]) * 0.5 * dx
    dissipated_energy = np.sum(areas_pos)

    thickness_crack = thickness
    if thickness == None:
        thickness_crack = crack_width

    GIC = dissipated_energy / (thickness_crack * crack_length)

    # Add title and labels
    plt.title(f"Energy: {round(dissipated_energy,4)} | Crack: {round(crack_length,4)}mm | GIC: {round(GIC,4)}N/mm")
    plt.xlabel("Displacement [mm]")
    plt.ylabel("Force [N]")
    plt.legend()

    # Display the plot
    plt.savefig(result_file)

    return FileResponse(result_file, media_type="image/png")


@router.get("/getPlot", operation_id="get_plot")
def get_plot(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: bool = False,
    output: str = "Output1",
    tasks: int = 1,
    # x_variable: str = "Time",
    # x_axis: str = "X",
    # x_absolute: bool = True,
    # y_variable: str = "External_Displacement",
    # y_axis: str = "X",
    # y_absolute: bool = True,
    request: Request = "",
) -> JSONResponse:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        log.warning("Results not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Results not found")

    resultpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    matching_files = FileHandler.get_all_output_files_with_extension(resultpath, model_name, output, ".csv")

    # x_data = Analysis.get_global_data(file, x_variable, x_axis, x_absolute)
    # y_data = Analysis.get_global_data(file, y_variable, y_axis, y_absolute)

    data = {}
    first_row = True
    # try:
    for file in matching_files:
        with open(file, "r", encoding="UTF-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if first_row:
                    # Extract column names from the first row
                    column_names = row
                    for idx, column_name in enumerate(column_names):
                        if len(matching_files) > 1:
                            column_names[idx] = column_name + "_" + file.split(".")[0].split("_")[-1]
                        data[column_names[idx]] = []

                    first_row = False
                else:
                    # Populate data dictionary with values
                    for i, value in enumerate(row):
                        data[column_names[i]].append(value)
        first_row = True
    return JSONResponse(content=data)
    # except IOError:
    #     log.error("%s results can not be found on %s", model_name, cluster)
    #     return ResponseModel(data=data, message=model_name + " results can not be found on " + cluster)


@router.get("/getResults", operation_id="get_results")
def get_results(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    tasks: int = 1,
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
            detail=model_name + " results can not be found on",
        )

    # resultpath = './simulations/' + os.path.join(username, model_name)
    resultpath = FileHandler.get_local_model_path(username, model_name)
    zip_file = os.path.join(resultpath, model_name + "_" + model_folder_name)

    # check if folder contains only one .e file
    if not all_data:
        for file in os.listdir(os.path.join(resultpath, model_folder_name)):
            if file.endswith(".e"):
                return FileResponse(os.path.join(resultpath, model_folder_name, file))

    try:
        print(zip_file)
        shutil.make_archive(zip_file, "zip", os.path.join(resultpath, model_folder_name))

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
        return model_name + " results can not be found"


def get_cell_data(variable, points, point_data, cell_data, block_data, displ_factor):
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

    return np_points_all_x, np_points_all_y, np_points_all_z, cell_value


def get_point_data(variable, axis, displ_factor, use_multi_data, points, point_data):
    np_first_points_x = np.array(points[:, 0])
    np_first_points_y = np.array(points[:, 1])
    np_first_points_z = np.array(points[:, 2])

    np_points_all_z = None

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
        if point_data.keys().__contains__(variable):
            cell_value = point_data[variable]
        else:
            cell_value = np.full_like(np_points_all_x, 0)

    return np_points_all_x, np_points_all_y, np_points_all_z, cell_value


@router.get("/getPointDataResults", operation_id="get_point_data_results")
def get_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    tasks: int = 1,
    cluster: bool = False,
    axis: str = "Magnitude",
    step: int = 78,
    displ_factor: float = 100,
    variable: str = "Displacements",
    filter: str = "",
    color_bar_min: float = None,
    color_bar_max: float = None,
    request: Request = "",
) -> PointDataResults:
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    if not os.path.exists(file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results can not be found, maybe they are not generated yet.",
        )
    number_of_steps = exodusreader.get_number_of_steps(file)

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
        try:
            (
                points,
                point_data,
                global_data,
                cell_data,
                ns,
                block_data,
                time,
            ) = exodusreader.read_timestep(file, number_of_steps)
        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Results can not be found, maybe they are not generated yet.",
            )

    use_cell_data = False

    variable_list = list(point_data.keys())
    variable_list = list(
        set([entry[:-1] if entry[-1].lower() in ["x", "y", "z"] else entry for entry in variable_list])
    )

    np_points_all_z = None
    use_multi_data = False

    if variable in [
        "Displacements",
        "Forces",
        "Strainx",
        "Strainy",
        "Strainz",
        "Cauchy Stressx",
        "Cauchy Stressy",
        "Cauchy Stressz",
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

    filter_value = []
    use_filter = len(filter) > 0

    if use_cell_data:
        np_points_all_x, np_points_all_y, np_points_all_z, cell_value = get_cell_data(
            points, point_data, cell_data, block_data, axis_id, variable
        )

    else:
        np_points_all_x, np_points_all_y, np_points_all_z, cell_value = get_point_data(
            variable, axis, displ_factor, use_multi_data, points, point_data
        )
        if use_filter:
            _, _, _, filter_value = get_point_data(
                filter,
                "Not_Magnitude",
                displ_factor,
                use_multi_data,
                points,
                point_data,
            )

    if np_points_all_z is None:
        np_points_all_z = np.zeros_like(np_points_all_x)

    if use_filter:
        cell_value = cell_value[filter_value != 0]
        np_points_all_x = np_points_all_x[filter_value != 0]
        np_points_all_y = np_points_all_y[filter_value != 0]
        np_points_all_z = np_points_all_z[filter_value != 0]

    if len(cell_value) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="All nodes are filtered out. Remove filter or change time value.",
        )

    min_cell_value = np.min(cell_value) if color_bar_min == None else color_bar_min
    max_cell_value = np.max(cell_value) if color_bar_max == None else color_bar_max
    if max_cell_value == min_cell_value:
        normalized_cell_value = np.zeros_like(cell_value)
    else:
        normalized_cell_value = (cell_value - min_cell_value) / (max_cell_value - min_cell_value)
    print(time)

    reduce_factor = 1
    if len(np_points_all_x) > max_nodes:
        reduce_factor = int(len(np_points_all_x) / max_nodes)
        log.info(f"Number of nodes in file is too large, only every {reduce_factor}th node is read!")

    data = PointDataResults(
        nodes=np.ravel(
            [np_points_all_x[::reduce_factor], np_points_all_y[::reduce_factor], np_points_all_z[::reduce_factor]],
            order="F",
        ).tolist(),
        value=normalized_cell_value.tolist()[::reduce_factor],
        variables=variable_list,
        number_of_steps=number_of_steps,
        min_value=min_cell_value,
        max_value=max_cell_value,
        time=np.format_float_scientific(time, 2),
    )
    # data = {
    #     "nodes": np.ravel(
    #         [np_points_all_x[::reduce_factor], np_points_all_y[::reduce_factor], np_points_all_z[::reduce_factor]],
    #         order="F",
    #     ).tolist(),
    #     "value": normalized_cell_value.tolist()[::reduce_factor],
    #     "variables": variable_list,
    #     "number_of_steps": number_of_steps,
    #     "min_value": min_cell_value,
    #     "max_value": max_cell_value,
    #     "time": np.format_float_scientific(time, 2),
    # }

    return data
