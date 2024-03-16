# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import time

import numpy as np
import paramiko
import pygalmesh
from fastapi import APIRouter, Request
from gcodereader import gcodereader

from support.base_models import ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/translate", tags=["Translate Methods"])


@router.post("/model")
def translate_model(
    file: str,
    model_name: str,
    model_folder_name: str = "Default",
    discretization: float = 2,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    start_time = time.time()

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    model_file = os.path.join(localpath, file)
    mesh = pygalmesh.generate_volume_mesh_from_surface_mesh(
        model_file,
        lloyd=True,
        odt=False,
        perturb=True,
        exude=True,
        max_edge_size_at_feature_edges=1.0,
        min_facet_angle=25,
        max_radius_surface_delaunay_ball=1.4,  # Adjusted for better volume meshing
        max_facet_distance=5,
        max_circumradius_edge_ratio=3,
        max_cell_circumradius=1.0,
        exude_sliver_bound=0.0,
        exude_time_limit=0.0,
        verbose=False,
        reorient=True,
        seed=0,
    )

    # Write the volume mesh to a VTK file
    # vtk_file = os.path.join(localpath,model_name+".vtk")
    # mesh.write(vtk_file)
    # Get volume elements and their nodes
    volume_elements = mesh.get_cells_type("tetra")
    nodes = mesh.points

    # Calculate volumes of tetrahedral elements
    def tetrahedron_volume(p1, p2, p3, p4):
        return np.abs(np.dot((p2 - p1), np.cross((p3 - p1), (p4 - p1)))) / 6

    element_volumes = []
    print(len(volume_elements))
    for element in volume_elements:
        p1, p2, p3, p4 = [nodes[i] for i in element]
        volume = tetrahedron_volume(p1, p2, p3, p4)
        element_volumes.append(volume)

    # Save elements and volumes to a text file
    txt_file = os.path.join(localpath, model_name + ".txt")
    with open(txt_file, "w") as file:
        file.write("#header: x y z block_id volume\n")
        for element, volume in zip(volume_elements, element_volumes):
            p1, p2, p3, p4 = nodes[element]
            centroid = np.mean([p1, p2, p3, p4], axis=0)
            file.write(f"{centroid[0]} {centroid[1]} {centroid[2]} {1} {volume}\n")

    log.info(
        "%s has been translated in %.2f seconds",
        model_name,
        time.time() - start_time,
    )
    return ResponseModel(
        data=True,
        message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
    )


@router.post("/gcode")
async def translate_gcode(
    model_name: str,
    discretization: float,
    dt: float,
    scale: float,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    start_time = time.time()

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)
    # output_path = FileHandler.get_local_user_path(username)

    gcodereader.read(model_name, localpath, localpath, discretization, dt, scale)

    log.info(
        "%s has been translated in %.2f seconds",
        model_name,
        time.time() - start_time,
    )
    return ResponseModel(
        data=True,
        message=f"{model_name} has been translated in {(time.time() - start_time):.2f} seconds",
    )
