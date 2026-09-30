# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "model_name",
    [
        "Dogbone",
        "CompactTension",
        # "DCBmodel",
        # "ENFmodel",
        # "Kalthoff-Winkler",
        # "PlateWithHole",
        # "PlateWithOpening",
        # "RingOnRing",
    ],
)
def test_generate_model(model_name):
    assets_path = "./models"

    with open(
        os.path.join(assets_path, model_name, model_name + ".json"),
        "r",
        encoding="UTF-8",
    ) as file:
        params = json.load(file)
    valves = client.get(f"/models/{model_name}/params").json()
    response = client.post(f"/workspaces/{model_name}/Default/generate", json={"data": params, "valves": valves})
    assert response.status_code == 200, response.text
