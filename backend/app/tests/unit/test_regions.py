# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import base64
import json
import zlib

import numpy as np
import pytest

from backend.app.support.base_models import ModelData
from backend.app.support.model import loader
from backend.app.support.model.regions import preview_regions
from backend.app.support.model.shapes import PRIMITIVES, Polygon
from backend.app.support.model.yaml_model import model_class


def _data(two_d=True, name=None):
    path = (
        loader.find_model(name)[0].parent / (name + ".json")
        if name
        else loader.APP_DIR / "assets" / "config_template.json"
    )
    with open(path, encoding="UTF-8") as file:
        data = ModelData(**json.load(file))
    data.model.twoDimensional = two_d
    return data


def _png_mask(b64):
    """Decode the (ny, nx) grayscale PNG written by regions._png, row 0 = lowest y."""
    png = base64.b64decode(b64)
    width, height = int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")
    idat, pos = b"", 8
    while pos < len(png):
        length, kind = int.from_bytes(png[pos : pos + 4], "big"), png[pos + 4 : pos + 8]
        if kind == b"IDAT":
            idat += png[pos + 8 : pos + 8 + length]
        pos += 12 + length
    rows = np.frombuffer(zlib.decompress(idat), dtype=np.uint8).reshape(height, width + 1)[:, 1:]
    return rows[::-1] > 127


def inside(region, x, y):
    """Evaluate a preview region at points, the way the frontend draws it."""
    kind = region["type"]
    if kind == "all":
        return np.ones_like(x, dtype=bool)
    if kind == "none":
        return np.zeros_like(x, dtype=bool)
    if kind == "halfplane":
        value = region["a"] * x + region["b"] * y
        return value < region["c"] if region["strict"] else value <= region["c"]
    if kind == "and":
        return np.logical_and.reduce([inside(c, x, y) for c in region["children"]])
    if kind == "or":
        return np.logical_or.reduce([inside(c, x, y) for c in region["children"]])
    if kind == "not":
        return ~inside(region["child"], x, y)
    if kind == "raster":
        mask = _png_mask(region["png"])
        ny, nx = mask.shape
        i = np.clip(((x - region["x0"]) / region["width"] * nx).astype(int), 0, nx - 1)
        j = np.clip(((y - region["y0"]) / region["height"] * ny).astype(int), 0, ny - 1)
        return mask[j, i]
    params = {k: v for k, v in region["shape"].items() if k not in ("type", "bounds")}
    kind = region["shape"]["type"]
    shape = Polygon(params["points"]) if kind == "polygon" else PRIMITIVES[kind](**params)
    return shape.contains(x, y, np.zeros_like(x))


def paint(regions, x, y):
    """Block id per point: 0 outside the body, 1 inside, then blocks in order (later wins)."""
    k = inside(regions["body"], x, y).astype(int)
    for block in regions["blocks"]:
        k = np.where(inside(block["region"], x, y) & (k > 0), block["id"], k)
    return k


YAML_BUILT_INS = ["DCBmodel", "ENFmodel", "PlateWithHole", "Kalthoff-Winkler", "CompactTension"]


@pytest.mark.parametrize("name", YAML_BUILT_INS)
def test_regions_reproduce_the_mesh_blocks_in_2d(name):
    model = loader.load_model(name)({}, _data(True, name))
    built = model.build()
    regions = preview_regions(model)
    assert "raster" not in json.dumps(regions), "built-in models are drawn exactly"
    np.testing.assert_array_equal(paint(regions, built["x"], built["y"]), built["block"])


def test_where_conditions_become_halfplanes():
    text = """
parameters: {L: 10}
geometry:
  spacing: 1
  add: [{box: {min: [0, 0, 0], max: [L, 4, 0]}}]
blocks:
  - {id: 2, where: "0 <= x <= L / 2 and not y > 3"}
  - {id: 3, where: "x + 2 * y < 5 or x == 1"}
"""
    regions = preview_regions(model_class(text)({}, _data()))
    first, second = (b["region"] for b in regions["blocks"])
    assert first == {
        "type": "and",
        "children": [
            {
                "type": "and",
                "children": [
                    {"type": "halfplane", "a": -1.0, "b": 0.0, "c": 0.0, "strict": False},
                    {"type": "halfplane", "a": 1.0, "b": 0.0, "c": 5.0, "strict": False},
                ],
            },
            {"type": "not", "child": {"type": "halfplane", "a": 0.0, "b": -1.0, "c": -3.0, "strict": True}},
        ],
    }
    assert second["children"][0] == {"type": "halfplane", "a": 1.0, "b": 2.0, "c": 5.0, "strict": True}
    assert second["children"][1] == {"type": "none"}, "x == 1 has no area; sampling finds nothing"


def test_curved_and_z_conditions_are_sampled():
    text = """
geometry:
  spacing: 0.5
  add: [{box: {min: [0, 0, 0], max: [10, 10, 4]}}]
blocks:
  - {id: 2, where: "(x - 5) ** 2 + (y - 5) ** 2 < 4"}
  - {id: 3, where: "z > 2"}
"""
    Model = model_class(text)
    flat = preview_regions(Model({}, _data(True)))["blocks"]
    assert flat[0]["region"]["type"] == "raster"
    assert flat[1]["region"] == {"type": "none"}, "in 2D z is 0, so z > 2 never holds"

    top = preview_regions(Model({}, _data(False)))["blocks"]
    assert top[1]["region"] == {"type": "all"}, "seen from above, every column reaches z > 2"
    circle = inside(top[0]["region"], np.array([5.0, 5.0, 9.0]), np.array([5.0, 6.5, 9.0]))
    assert circle.tolist() == [True, True, False]


def test_2d_slices_shapes_at_z0():
    text = """
geometry:
  spacing: 0.5
  add:
    - box: {min: [0, 0, -1], max: [10, 10, 1]}
    - sphere: {center: [20, 5, 3], radius: 5}
    - box: {min: [0, 20, 2], max: [5, 25, 3]}
"""
    body = preview_regions(model_class(text)({}, _data(True)))["body"]
    box, sphere, off_plane = body["children"]
    assert box["shape"]["type"] == "box"
    assert sphere["shape"]["type"] == "sphere" and sphere["shape"]["radius"] == pytest.approx(4), "cut at z = 0"
    assert off_plane == {"type": "none"}


def test_python_array_blocks_are_sampled_and_point_cloud_models_have_no_regions():
    dogbone = loader.load_model("Dogbone")({}, _data(True, "Dogbone"))
    assert preview_regions(dogbone) is None

    class Layers(loader.PeriHubModel):
        spacing = 1.0

        def geometry(self):
            return PRIMITIVES["box"]([0, 0, 0], [10, 4, 2])

        def blocks(self, x, y, z):
            return {2: y > 2, 3: PRIMITIVES["sphere"]([5, 2, 0], 1)}

    regions = preview_regions(Layers({}, _data(True)))["blocks"]
    assert regions[0]["region"]["type"] == "raster"
    assert regions[1]["region"]["shape"]["type"] == "sphere"
