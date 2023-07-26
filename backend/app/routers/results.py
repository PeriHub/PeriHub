# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import FileResponse

from support.base_models import ResponseModel
from support.export.image_export import ImageExport
from support.export.video_export import VideoExport
from support.file_handler import FileHandler
from support.globals import dev, log
from support.results.analysis import Analysis
from support.results.crack_analysis import CrackAnalysis

router = APIRouter(prefix="/results", tags=["Results Methods"])


@router.get("/getImagePython")
def get_image_python(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    tasks: int = 32,
    output: str = "Output1",
    variable: str = "Displacement",
    axis: str = "X",
    displ_factor: int = 20,
    marker_size: int = 16,
    length: float = 0.13,
    height: float = 0.02,
    triangulate: bool = False,
    dx_value: float = 0.004,
    step: int = -1,
    cb_left: Optional[bool] = False,
    transparent: Optional[bool] = True,
    three_d: Optional[bool] = False,
    elevation: Optional[float] = 30,
    azimuth: Optional[float] = 30,
    roll: Optional[float] = 0,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    if model_name in ["ENFmodel"]:
        height *= 2

    # try:
    filepath = ImageExport.get_result_image_from_exodus(
        file,
        displ_factor,
        marker_size,
        variable,
        axis,
        length,
        height,
        triangulate,
        dx_value,
        step,
        cb_left,
        transparent,
        three_d,
        elevation,
        azimuth,
        roll,
    )
    # except ValueError:
    #     log.error("%s ValueError %s", model_name, cluster)
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="ValueError",
    #     )

    try:
        return FileResponse(filepath)
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=model_name + " results can not be found on " + cluster,
        )


@router.get("/getPlotPython")
def get_plot_python(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    tasks: int = 32,
    output: str = "Output1",
    x_variable: str = "Time",
    x_axis: str = "X",
    y_variable: str = "External_Displacement",
    y_axis: str = "X",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    filepath = ImageExport.get_plot_image_from_exodus(file, x_variable, x_axis, y_variable, y_axis)

    try:
        return FileResponse(filepath)
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


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
    cluster: str = "None",
    tasks: int = 32,
    output: str = "Output1",
    step: int = -1,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
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


@router.get("/getGif")
def get_gif(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    output: str = "Output1",
    tasks: int = 32,
    variable: str = "Displacement",
    axis: str = "X",
    apply_displacements: bool = False,
    displ_factor: int = 200,
    max_edge_distance: float = 2.0,
    length: float = 4.4,
    height: float = 1.1,
    fps: int = 2,
    dpi: int = 100,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    size: Optional[float] = 20,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    filepath = VideoExport.get_gif_from_exodus(
        file,
        apply_displacements,
        displ_factor,
        max_edge_distance,
        variable,
        axis,
        length,
        height,
        fps,
        dpi,
        x_min,
        x_max,
        y_min,
        y_max,
        size,
    )

    try:
        return FileResponse(filepath)
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


@router.get("/getTriangulatedMeshFromExodus")
def get_triangulated_mesh_from_exodus(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    output: str = "Output1",
    tasks: int = 32,
    displ_factor: int = 10,
    timestep: int = -1,
    max_edge_distance: float = 0.5,
    length: float = 0.13,
    height: float = 0.02,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name + model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    filepath = VideoExport.get_triangulated_mesh_from_exodus(
        file,
        displ_factor,
        timestep,
        max_edge_distance,
        length,
        height,
    )

    try:
        return FileResponse(filepath)
    except IOError:
        log.error("%s results can not be found on %s", model_name, cluster)
        return model_name + " results can not be found on " + cluster


@router.get("/getPlot")
def get_plot(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    cluster: str = "None",
    output: str = "Output1",
    tasks: int = 32,
    x_variable: str = "Time",
    x_axis: str = "X",
    x_absolute: bool = True,
    y_variable: str = "External_Displacement",
    y_axis: str = "X",
    y_absolute: bool = True,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, False, tasks, output
    ):
        raise IOError  # NotFoundException(name=model_name)

    resultpath = "./Results/" + os.path.join(username, model_name, model_folder_name)
    file = os.path.join(resultpath, model_name + "_" + output + ".e")

    x_data = Analysis.get_global_data(file, x_variable, x_axis, x_absolute)
    y_data = Analysis.get_global_data(file, y_variable, y_axis, y_absolute)

    return ResponseModel(data=[x_data, y_data], message="Plot received")


@router.get("/getResults")
def get_results(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    tasks: int = 32,
    cluster: str = "None",
    all_data: bool = False,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    if not FileHandler.copy_results_from_cluster(
        username, model_name, model_folder_name, cluster, all_data, tasks, output
    ):
        raise HTTPException(
            status_code=404,
            detail=model_name + " results can not be found on " + cluster,
        )

    # resultpath = './Results/' + os.path.join(username, model_name)
    userpath = "./Results/" + username
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
