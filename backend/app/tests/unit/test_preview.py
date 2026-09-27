# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import generate

client = TestClient(app)

BUILT_IN = sorted(d for d in os.listdir("./models") if os.path.isfile(os.path.join("./models", d, d + ".json")))


def _body(model_name):
    with open(os.path.join("./models", model_name, model_name + ".json"), encoding="UTF-8") as file:
        data = json.load(file)
    valves = client.get("/model/getValves", params={"model_name": model_name}).json()
    return {"data": data, "valves": valves}


@pytest.mark.parametrize("model_name", BUILT_IN)
def test_preview_built_in_models(model_name):
    response = client.post("/generate/preview", params={"model_name": model_name}, json=_body(model_name))
    assert response.status_code == 200, response.text
    body = response.json()
    n = len(body["x"])
    assert 0 < n <= generate.PREVIEW_MAX_POINTS
    assert len(body["y"]) == len(body["z"]) == len(body["block"]) == n
    block_ids = {b["blocksId"] for b in _body(model_name)["data"]["blocks"]}
    assert set(body["block"]) <= block_ids


def test_preview_caps_discretization(monkeypatch):
    seen = {}
    real = generate.build_point_cloud

    def spy(model_name, data, valves_dict):
        seen.update(valves_dict)
        return real(model_name, data, valves_dict)

    monkeypatch.setattr(generate, "build_point_cloud", spy)
    body = _body("Dogbone")
    for valve in body["valves"]["valves"]:
        if valve["name"] == "DISCRETIZATION":
            valve["value"] = 500
    assert client.post("/generate/preview", params={"model_name": "Dogbone"}, json=body).status_code == 200
    assert seen["DISCRETIZATION"] == generate.PREVIEW_MAX_DISCRETIZATION


def test_preview_generator_error_is_422(monkeypatch):
    def boom(*_):
        raise ValueError("notch longer than part")

    monkeypatch.setattr(generate, "build_point_cloud", boom)
    response = client.post("/generate/preview", params={"model_name": "Dogbone"}, json=_body("Dogbone"))
    assert response.status_code == 422
    assert response.json()["detail"] == "notch longer than part"


def test_preview_unknown_model_is_404():
    response = client.post("/generate/preview", params={"model_name": "NoSuchModel"}, json=_body("Dogbone"))
    assert response.status_code == 404
