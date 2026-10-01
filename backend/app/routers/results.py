# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import csv
import io
import os
import shutil
from typing import Optional

import matplotlib
import numpy as np
from exodusreader import exodusreader
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse, Response

from ..db import base as db_base
from ..db.models import JobQueueEntry
from ..support.base_models import AnalysisRequest, PointDataResults
from ..support.db_auth import resolve_user
from ..support.file_handler import FileHandler
from ..support.globals import log, max_nodes
from ..support.guest import require_non_guest, user_folder
from ..support.job_queue import perilab_job_ids
from ..support.model import loader
from ..support.model.model_api import AnalysisContext
from ..support.model.point_cloud import valves_to_dict
from ..support.solver_backend import get_solver_backend
from .jobs import _can_view_entry, _latest_entry

matplotlib.use("Agg")  # analyses render in worker threads; never an interactive backend
import matplotlib.pyplot as plt  # noqa: E402

router = APIRouter(prefix="/results", tags=["Results Methods"])


def _result_folder(request: Request, model_name: str, model_folder_name: str, run_id: Optional[str]) -> str:
    """PeriLab writes a job's output to simulations/<perilab_job_id>/. That
    folder is only readable here when the solver runs locally (shared volume);
    `run_id` picks the run, else the folder's latest run is used."""

    def not_found(detail: str):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    if db_base.SessionLocal is None or not get_solver_backend().shares_local_filesystem:
        raise not_found("Results are only available when PeriLab runs locally.")
    with db_base.SessionLocal() as db:
        identity = resolve_user(request, db)
        if identity.user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
        if run_id:
            entry = db.get(JobQueueEntry, run_id)
            if entry is not None and not _can_view_entry(identity, entry):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your run.")
        else:
            entry = _latest_entry(db, identity.user.id, model_name, model_folder_name)
        job_ids = perilab_job_ids(entry) if entry else []
    if not job_ids:
        raise not_found("No run found for this model.")
    job_folder = os.path.join(FileHandler.get_local_simulation_path(), job_ids[0])
    if not os.path.isdir(job_folder):
        raise not_found("Results can not be found, maybe they are not generated yet.")
    return job_folder


@router.post(
    "/analysis",
    operation_id="run_analysis",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}, "description": "The analysis image"}},
    dependencies=[Depends(require_non_guest)],
)
def run_analysis(
    body: AnalysisRequest,
    model_name: str,
    analysis_id: str,
    model_folder_name: str = "Default",
    run_id: Optional[str] = None,
    request: Request = "",
):
    """Run one of the model's @analysis functions on a run's results; returns the image as PNG."""
    try:
        analyses = loader.load_analyses(model_name)
        param_list = loader.load_model(model_name).params()
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    fn = analyses.get(analysis_id)
    if fn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model_name} has no analysis {analysis_id}")

    result_dir = _result_folder(request, model_name, model_folder_name, run_id)
    params = valves_to_dict(body.valves)
    params = {p.name: p.cast(params[p.name]) if p.name in params else p.default for p in param_list}
    analysis_params = {
        p.name: p.cast(body.analysis_params[p.name]) if p.name in body.analysis_params else p.default
        for p in fn.perihub_analysis["params"]
    }
    ctx = AnalysisContext(params, analysis_params, result_dir, model_name, body.data)
    try:
        return Response(content=analysis_png(fn(ctx), result_dir), media_type="image/png")
    except Exception as e:
        log.warning("Analysis %s of %s failed: %s", analysis_id, model_name, e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"{type(e).__name__}: {e}")


def analysis_png(result, result_dir: str) -> bytes:
    """PNG bytes of what an @analysis function returned: a matplotlib Figure, or the path of
    an image it wrote — which must be inside the run's result folder."""
    if hasattr(result, "savefig"):
        buffer = io.BytesIO()
        result.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close(result)  # no-op for Figure(), frees pyplot figures
        return buffer.getvalue()
    if isinstance(result, (str, os.PathLike)):
        path = os.path.realpath(result if os.path.isabs(result) else os.path.join(result_dir, result))
        root = os.path.realpath(result_dir)
        if os.path.commonpath([path, root]) != root:
            raise ValueError("the analysis returned a file outside the result folder")
        if not os.path.isfile(path):
            raise ValueError(f"the analysis returned {os.path.basename(path)}, which does not exist")
        with open(path, "rb") as file:
            return file.read()
    raise ValueError(f"an analysis must return a matplotlib Figure or an image path, not {type(result).__name__}")


@router.get("/plot", operation_id="get_plot", response_model=dict[str, list[float | str]])
def get_plot(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    deviations_enabled: bool = False,
    # x_variable: str = "Time",
    # x_axis: str = "X",
    # x_absolute: bool = True,
    # y_variable: str = "External_Displacement",
    # y_axis: str = "X",
    # y_absolute: bool = True,
    run_id: Optional[str] = None,
    request: Request = "",
) -> JSONResponse:
    """A run's global CSV output as `{column: values}` for the charts. With `deviations_enabled`, every deviation
    run's CSV is included and its columns are suffixed with the run's number."""
    resultpath = _result_folder(request, model_name, model_folder_name, run_id)

    matching_files = FileHandler.get_all_output_files_with_extension(
        resultpath, model_name, output, ".csv", deviations_enabled
    )

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
                    # Populate data dictionary with values. Values come out of
                    # csv.reader as strings (e.g. "0.00", "1.000000E+02"); cast
                    # to float so the frontend receives real numbers and can
                    # compute a correct numeric axis domain instead of doing a
                    # lexicographic string comparison ("10.0" < "9.0").
                    for i, value in enumerate(row):
                        try:
                            parsed_value = float(value)
                        except ValueError:
                            log.warning(
                                "Non-numeric value %r in column %s of %s; keeping as string",
                                value,
                                column_names[i],
                                file,
                            )
                            parsed_value = value
                        data[column_names[i]].append(parsed_value)
        first_row = True
    return JSONResponse(content=data)
    # except IOError:
    #     log.error("%s results can not be found on %s", model_name, cluster)
    #     return ResponseModel(data=data, message=model_name + " results can not be found on " + cluster)


@router.get("/download", operation_id="get_results")
def get_results(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    all_data: bool = False,
    run_id: Optional[str] = None,
    request: Request = "",
):
    """Download a run's results: the Exodus `.e` file, or with `all_data` (or when there is none) the whole result
    folder as a zip."""
    username = user_folder(request)

    resultpath = FileHandler.get_local_model_path(username, model_name)
    zip_file = os.path.join(resultpath, model_name + "_" + model_folder_name)
    result_folder = _result_folder(request, model_name, model_folder_name, run_id)

    # check if folder contains only one .e file
    if not all_data:
        for file in os.listdir(result_folder):
            if file.endswith(".e"):
                return FileResponse(os.path.join(result_folder, file))

    try:
        shutil.make_archive(zip_file, "zip", result_folder)

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
        log.error("%s results can not be found", model_name)
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
    """Result points displaced by `displ_factor` times the displacements, plus the values of `variable`."""
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


@router.get("/points", operation_id="get_point_data_results")
def get_data(
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    output: str = "Output1",
    axis: str = "Magnitude",
    step: int = 78,
    displ_factor: float = 100,
    variable: str = "Displacements",
    filter: str = "",
    color_bar_min: Optional[float] = None,
    color_bar_max: Optional[float] = None,
    run_id: Optional[str] = None,
    request: Request = "",
) -> PointDataResults:
    """One time step of a run's Exodus output for the 3D view: points displaced by `displ_factor` and the values of
    `variable`/`axis`, optionally clamped to the color-bar range and restricted to points where the `filter`
    variable is non-zero. Falls back to the last step when `step` is out of range, and to the first available
    variable when `variable` doesn't exist."""
    resultpath = _result_folder(request, model_name, model_folder_name, run_id)
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

    if variable not in variable_list:
        log.warning(f"Variable {variable} not found, using first available: {variable_list[0]}")
        variable = variable_list[0]

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
    # print(time)

    reduce_factor = 1
    if len(np_points_all_x) > max_nodes:
        reduce_factor = int(len(np_points_all_x) / max_nodes)
        log.info(f"Number of nodes in file is too large, only every {reduce_factor}th node is read!")
    # print(normalized_cell_value.tolist()[::reduce_factor])
    data = PointDataResults(
        nodes=np.ravel(
            [np_points_all_x[::reduce_factor], np_points_all_y[::reduce_factor], np_points_all_z[::reduce_factor]],
            order="F",
        ).tolist(),
        value=cell_value.tolist()[::reduce_factor],
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
