# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import time
from typing import Optional

import numpy as np
from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import BaseModel

# from ..models.PlateWithHole.plate_with_hole import PlateWithHole
# from ..models.PlateWithOpening.plate_with_opening import PlateWithOpening
# from ..models.RingOnRing.ring_on_ring import RingOnRing
# from ..models.Smetana.smetana import Smetana
from ..db import base
from ..support.base_models import Block, Deviations, ModelData, Valves
from ..support.file_handler import FileHandler
from ..support.globals import log
from ..support.guest import DB_LESS_USER, GUEST_DENIED, apply_guest_limits, current_user, guest_limits
from ..support.model.point_cloud import build_point_cloud, valves_to_dict
from ..support.model.yaml_model import ModelSpecError
from ..support.writer.model_writer import ModelWriter

# from ..models.KalthoffWinkler.kalthoff_winkler import KalthoffWinkler
# from ..models.OwnModel.own_model import OwnModel


# from ..models.DCBmodel.dcb_model import DCBmodel
# from ..models.Dogbone.dogbone import Dogbone
# from ..models.ENFmodel.enf_model import ENFmodel
# from ..models.G1Cmodel.g1c_model import G1Cmodel


router = APIRouter(tags=["Generate Methods"])

ACCOUNT_MAX_NODES = 1_000_000  # node cap for real accounts; guests use the guest_max_nodes setting


@router.post("/workspaces/{model_name}/{model_folder_name}/generate", operation_id="generate_model")
def generate_model(
    data: ModelData,
    valves: Valves,
    model_name: str = "Dogbone",
    model_folder_name: str = "Default",
    request: Request = "",
):  # material: dict, Output: dict):
    """Generate the model into its folder: save the ModelData JSON, build the point cloud with the model's generator
    (skipped for `meshSource == "upload"`, which brings its own mesh), then write mesh, node sets and the PeriLab
    input deck. 404 if the generator is missing or the point count exceeds the caller's node limit, 422 if an
    uploaded mesh is expected but missing from the folder."""

    # With a DB every caller must be logged in, else the guest limits could be skipped by leaving out the token.
    # Without a DB (local dev, no accounts) everything goes to the single DB_LESS_USER folder.
    user = current_user(request)
    if base.SessionLocal is not None and user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    username = user.id if user is not None else DB_LESS_USER
    limits = None
    if user is not None and user.role == "guest":
        with base.SessionLocal() as db:
            limits = guest_limits(db)
    max_nodes = limits["max_nodes"] if limits else ACCOUNT_MAX_NODES
    if limits:
        if data.deviations is not None and data.deviations.enabled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=GUEST_DENIED)
        apply_guest_limits(data, limits)

    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    uploaded_mesh = data.model.meshSource == "upload"
    if uploaded_mesh and (not data.model.meshFile or not os.path.isfile(os.path.join(localpath, data.model.meshFile))):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="No mesh uploaded for this model")

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

    if not uploaded_mesh:

        valves_dict = valves_to_dict(valves)
        try:
            cloud = build_point_cloud(model_name, data, valves_dict)
        except LookupError as e:
            log.error(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ModelSpecError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
        dx_value, vol, k = cloud["dx"], cloud["volume"], cloud["block"]
        x_value, y_value, z_value = cloud["x"], cloud["y"], cloud["z"]

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
    if not uploaded_mesh:
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


class PreviewBlock(BaseModel):
    id: int
    bounds: dict[str, float]
    labelX: float
    labelY: float


class PreviewResponse(BaseModel):
    x: list[float]
    y: list[float]
    z: list[float]
    block: list[int]
    bounds_min: list[float]
    bounds_max: list[float]
    # Outlines of the model's primitives (see shapes.flatten) and per-block bounds/label anchor,
    # computed from the full-resolution cloud before it is thinned for the response.
    shapes: list[dict] = []
    blocks: list[PreviewBlock] = []
    # Exact drawing (support/model/regions.py): the body and each block as a region tree.
    # Null for models that make their own point cloud; the frontend then draws the points.
    regions: Optional[dict] = None


@router.post("/models/{model_name}/preview", operation_id="preview_model")
def preview_model(
    data: ModelData,
    valves: Valves,
    model_name: str = "Dogbone",
    source: Optional[str] = Body(default=None, description="Unsaved YAML model text (editor preview)"),
) -> PreviewResponse:
    """Coarse point cloud with block ids, drawn by the frontend as the model preview.

    Runs the generator exactly like /workspaces/{model}/{folder}/generate but with DISCRETIZATION capped and
    without writing anything, so it needs no user folder and works without an account. With
    `source`, the model comes from that YAML text instead of the saved file.
    """
    full_valves = valves_to_dict(valves)
    valves_dict = dict(full_valves)
    if "DISCRETIZATION" in valves_dict:
        valves_dict["DISCRETIZATION"] = min(valves_dict["DISCRETIZATION"], PREVIEW_MAX_DISCRETIZATION)

    try:
        cloud = build_point_cloud(model_name, data, valves_dict, source=source, region_valves=full_valves)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        log.warning("Preview of %s failed: %s", model_name, e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e) or type(e).__name__)

    x, y, z, k = (np.asarray(cloud[key]).ravel() for key in ("x", "y", "z", "block"))
    if len(x) == 0:
        return PreviewResponse(x=[], y=[], z=[], block=[], bounds_min=[0, 0, 0], bounds_max=[0, 0, 0])
    points = np.vstack([x, y, z]).astype(float)
    bounds_min, bounds_max = points.min(axis=1).tolist(), points.max(axis=1).tolist()

    if not data.model.twoDimensional:
        # The preview is a view from +z: keep the top-most point per x/y position, so thinning
        # below doesn't mix layers into stripes and the visible blocks are the top ones.
        order = np.lexsort((-points[2], np.round(points[1], 6), np.round(points[0], 6)))
        xy = np.round(points[:2, order], 6)
        first = np.ones(len(order), dtype=bool)
        first[1:] = np.any(xy[:, 1:] != xy[:, :-1], axis=0)
        points, k = points[:, order[first]], k[order[first]]
        x = points[0]

    if len(x) > PREVIEW_MAX_POINTS:
        # Even stride rather than random, so every block keeps proportional coverage.
        idx = np.linspace(0, len(x) - 1, PREVIEW_MAX_POINTS).astype(int)
        points, k = points[:, idx], k[idx]

    rounded = [[float(f"{v:.4g}") for v in row] for row in points]
    return PreviewResponse(
        x=rounded[0],
        y=rounded[1],
        z=rounded[2],
        block=k.astype(int).tolist(),
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        shapes=cloud["shapes"],
        blocks=cloud["blocks"],
        regions=cloud["regions"],
    )
