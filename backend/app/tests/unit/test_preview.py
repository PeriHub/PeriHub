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
    # Block bounds/labels come from the full-resolution cloud, one entry per block present.
    assert {b["id"] for b in body["blocks"]} == set(body["block"])
    for b in body["blocks"]:
        assert b["bounds"]["minX"] <= b["labelX"] <= b["bounds"]["maxX"]


def test_preview_caps_discretization(monkeypatch):
    seen = {}
    real = generate.build_point_cloud

    def spy(model_name, data, valves_dict, **kwargs):
        seen.update(valves_dict)
        return real(model_name, data, valves_dict, **kwargs)

    monkeypatch.setattr(generate, "build_point_cloud", spy)
    body = _body("Dogbone")
    for valve in body["valves"]["valves"]:
        if valve["name"] == "DISCRETIZATION":
            valve["value"] = 500
    assert client.post("/generate/preview", params={"model_name": "Dogbone"}, json=body).status_code == 200
    assert seen["DISCRETIZATION"] == generate.PREVIEW_MAX_DISCRETIZATION


def test_preview_generator_error_is_422(monkeypatch):
    def boom(*_, **__):
        raise ValueError("notch longer than part")

    monkeypatch.setattr(generate, "build_point_cloud", boom)
    response = client.post("/generate/preview", params={"model_name": "Dogbone"}, json=_body("Dogbone"))
    assert response.status_code == 422
    assert response.json()["detail"] == "notch longer than part"


def test_preview_unknown_model_is_404():
    response = client.post("/generate/preview", params={"model_name": "NoSuchModel"}, json=_body("Dogbone"))
    assert response.status_code == 404


def test_preview_from_unsaved_yaml_source():
    source = """
title: Draft
parameters:
  DISCRETIZATION: 10
geometry:
  spacing: 1
  add:
    - box: {min: [0, 0, 0], max: [10, 4, 0]}
  remove:
    - sphere: {center: [5, 2, 0], radius: 1.5}
blocks:
  - {id: 2, box: {min: [8, 0, 0], max: [10, 4, 0]}}
"""
    body = {**_body("Dogbone"), "source": source}
    response = client.post("/generate/preview", params={"model_name": "Draft"}, json=body)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["bounds_min"][:2] == [0, 0] and result["bounds_max"][:2] == [10, 4]
    assert [(s["role"], s["type"]) for s in result["shapes"]] == [
        ("add", "box"),
        ("remove", "sphere"),
        ("block", "box"),
    ]
    block2 = next(b for b in result["blocks"] if b["id"] == 2)
    assert block2["bounds"] == {"minX": 8, "maxX": 10, "minY": 0, "maxY": 4}


def test_preview_bad_yaml_source_is_422_with_path():
    body = {**_body("Dogbone"), "source": "geometry:\n  spacing: 1\n  add:\n    - sphere: {center: [0, 0, 0]}\n"}
    response = client.post("/generate/preview", params={"model_name": "Draft"}, json=body)
    assert response.status_code == 422
    assert response.json()["detail"].startswith("geometry.add[0].sphere: wrong arguments")


def test_3d_preview_is_a_top_view():
    body = _body("PlateWithHole")
    body["data"]["model"]["twoDimensional"] = False
    response = client.post("/generate/preview", params={"model_name": "PlateWithHole"}, json=body)
    assert response.status_code == 200, response.text
    result = response.json()
    xy = list(zip(result["x"], result["y"]))
    assert len(xy) == len(set(xy)), "one point per x/y position"
    assert result["bounds_min"][2] < result["bounds_max"][2], "bounds still cover the full thickness"
