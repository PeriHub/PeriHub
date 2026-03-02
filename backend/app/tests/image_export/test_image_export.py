# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_getPointData():
    test_path = "./tests/image_export/"
    file_name = "Dogbone_Output1.e"
    remote_path = "./simulations/guest/Dogbone/Default"

    os.makedirs(remote_path, exist_ok=True)
    shutil.copy(
        os.path.join(test_path, file_name),
        os.path.join(remote_path, file_name),
    )

    response = client.get("/results/getPointData")
    assert response.json()["number_of_steps"] == 46
    shutil.rmtree("./simulations")


def test_getPlot():
    test_path = "./tests/image_export/"
    file_name = "Dogbone_Output1.e"
    remote_path = "./simulations/guest/Dogbone/Default"

    os.makedirs(remote_path, exist_ok=True)
    shutil.copy(
        os.path.join(test_path, file_name),
        os.path.join(remote_path, file_name),
    )

    response = client.get(
        "/results/getPlot",
        params={
            "model_name": "Dogbone",
            "model_folder_name": "Default",
            "output": "Output1",
            "tasks": 1,
        },
    )
    assert response.status_code == 200
    assert "Time" in response.json()
    shutil.rmtree("./simulations")
