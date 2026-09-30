# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import shutil
from types import SimpleNamespace

import netCDF4
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers.model import get_workspace_file
from backend.app.support.base_models import Model
from backend.app.support.file_handler import FileHandler
from backend.app.support.model import mesh_readers

client = TestClient(app)

USER = "pytest_mesh_source"
MODEL = "UploadedMesh"
HEADERS = {"userName": USER}


@pytest.fixture
def folder():
    path = FileHandler.get_local_model_folder_path(USER, MODEL, "Default")
    os.makedirs(path, exist_ok=True)
    yield path
    shutil.rmtree(FileHandler.get_local_user_path(USER), ignore_errors=True)


def _write_exodus(path):
    # 4 nodes, two SPHERE blocks: nodes 1-2 in block 1, nodes 3-4 in block 2.
    with netCDF4.Dataset(path, "w") as nc:
        nc.createDimension("num_nodes", 4)
        nc.createDimension("num_el_in_blk1", 2)
        nc.createDimension("num_el_in_blk2", 2)
        nc.createDimension("num_nod_per_el1", 1)
        for name, values in (("coordx", [0, 1, 2, 3]), ("coordy", [0, 0, 1, 1]), ("coordz", [0, 0, 0, 5])):
            nc.createVariable(name, "f8", ("num_nodes",))[:] = values
        for i, nodes in ((1, [[1], [2]]), (2, [[3], [4]])):
            var = nc.createVariable(f"connect{i}", "i4", (f"num_el_in_blk{i}", "num_nod_per_el1"))
            var.elem_type = "SPHERE"
            var[:] = nodes


def test_model_migrates_legacy_own_model():
    assert Model(modelFolderName="D", twoDimensional=True, ownModel=True, ownMesh=None).meshSource == "upload"
    assert Model(modelFolderName="D", twoDimensional=True, ownModel=False).meshSource == "model"
    assert Model(modelFolderName="D", twoDimensional=True).meshSource == "model"
    assert "ownModel" not in Model(modelFolderName="D", twoDimensional=True, ownModel=True).model_dump()


def _upload_body(mesh_file):
    with open("./models/Dogbone/Dogbone.json", encoding="UTF-8") as file:
        data = json.load(file)
    data["model"].update(meshSource="upload", meshFile=mesh_file)
    return {"data": data, "valves": {"valves": []}}


@pytest.mark.parametrize("mesh_file", [None, "missing.txt", "../Dogbone.json"])
def test_generate_rejects_missing_uploaded_mesh(folder, mesh_file):
    response = client.post(f"/workspaces/{MODEL}/Default/generate", json=_upload_body(mesh_file), headers=HEADERS)
    assert response.status_code == 422, response.text
    assert response.json()["detail"] == "No mesh uploaded for this model"


def test_generate_accepts_uploaded_mesh(folder):
    with open(os.path.join(folder, "mesh.txt"), "w", encoding="UTF-8") as file:
        file.write("header: x y block_id volume\n0 0 1 1\n1 0 1 1\n")
    response = client.post(f"/workspaces/{MODEL}/Default/generate", json=_upload_body("mesh.txt"), headers=HEADERS)
    assert response.status_code == 200, response.text


def test_read_points_txt(tmp_path):
    path = tmp_path / "mesh.txt"
    path.write_text("header: x y z block_id volume\n# comment\n0 0 0.5 1 1\n1 2 3 2 1\n")
    xyz, block = mesh_readers.read_points(str(path), two_d=False)
    assert xyz.tolist() == [[0, 0, 0.5], [1, 2, 3]]
    assert block.tolist() == [1, 2]
    with pytest.raises(ValueError):
        mesh_readers.read_points(str(path), two_d=True)  # third column is z, not an integer block id


def test_read_points_exodus(tmp_path):
    path = str(tmp_path / "mesh.g")
    _write_exodus(path)
    xyz, block = mesh_readers.read_points(path, two_d=False)
    assert xyz.tolist() == [[0, 0, 0], [1, 0, 0], [2, 1, 0], [3, 1, 5]]
    assert block.tolist() == [1, 1, 2, 2]


def test_read_points_rejects_gcode(tmp_path):
    with pytest.raises(ValueError):
        mesh_readers.read_points(str(tmp_path / "part.gcode"), two_d=False)


def test_point_data_of_uploaded_exodus(folder):
    _write_exodus(os.path.join(folder, "mesh.e"))
    response = client.get(
        f"/workspaces/{MODEL}/Default/points", params={"mesh_file": "mesh.e", "two_d": False}, headers=HEADERS
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["points"]) == 12
    assert body["block_ids"] == [0.5, 0.5, 1.0, 1.0]


def test_workspace_file(folder):
    with open(os.path.join(folder, "part.gcode"), "w", encoding="UTF-8") as file:
        file.write("G1 X1 Y1 E1\n")
    response = client.get(f"/workspaces/{MODEL}/Default/files/part.gcode", headers=HEADERS)
    assert response.status_code == 200
    assert response.text == "G1 X1 Y1 E1\n"
    # HTTP clients normalize `..` away, so call the handler directly for the traversal check.
    with pytest.raises(HTTPException) as error:
        get_workspace_file(MODEL, "Default", "..", SimpleNamespace(headers=HEADERS))
    assert error.value.status_code == 404
    assert client.get(f"/workspaces/{MODEL}/Default/files/missing.gcode", headers=HEADERS).status_code == 404
