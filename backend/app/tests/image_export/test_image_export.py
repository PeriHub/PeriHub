# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil

from fastapi.testclient import TestClient

from app.api_main import app

client = TestClient(app)


def test_getPointData():
    test_path = "./tests/image_export/"
    file_name = "Dogbone_Output1.e"
    remote_path = "./Results/guest/Dogbone/Default"

    os.makedirs(remote_path, exist_ok=True)
    shutil.copy(
        os.path.join(test_path, file_name),
        os.path.join(remote_path, file_name),
    )

    response = client.get("/results/getPointData")
    assert response.json()["number_of_steps"] == 46
    shutil.rmtree("./Results")
