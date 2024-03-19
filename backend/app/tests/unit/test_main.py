# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

import pytest
from fastapi.testclient import TestClient

from app.api_main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "model_name",
    [
        "Dogbone",
        # "CompactTension",
        # "DCBmodel",
        # "ENFmodel",
        # "Kalthoff-Winkler",
        # "PlateWithHole",
        # "PlateWithOpening",
        # "RingOnRing",
    ],
)
def test_generate_model(model_name):
    assets_path = "./assets/models"

    with open(
        os.path.join(assets_path, model_name, model_name + ".json"),
        "r",
        encoding="UTF-8",
    ) as file:
        params = json.load(file)
    response = client.post("/generate/model?model_name=" + model_name, json=params)
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    assert response.status_code == 200
    assert response.json()["data"]
