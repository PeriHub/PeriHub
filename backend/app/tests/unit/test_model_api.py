# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import textwrap

import numpy as np
import pytest

from backend.app.support.base_models import ModelData
from backend.app.support.model import loader
from backend.app.support.model.expr import ExpressionError, evaluate
from backend.app.support.model.shapes import Box, Cone, Cylinder, Ellipsoid, Polygon, Sphere
from backend.app.support.model.yaml_model import ModelSpecError, model_class


def _data(two_d=True):
    with open(loader.APP_DIR / "assets" / "config_template.json", encoding="UTF-8") as file:
        data = ModelData(**json.load(file))
    data.model.twoDimensional = two_d
    return data


def _inside(shape, *points):
    p = np.array(points, dtype=float)
    return shape.contains(p[:, 0], p[:, 1], p[:, 2]).tolist()


# --- shapes ------------------------------------------------------------------------------------


def test_primitives_inside_tests_and_bounds():
    box = Box([0, 0, 0], [2, 1, 1])
    assert _inside(box, [2, 1, 1], [1, 0.5, 0.5], [2.01, 0, 0]) == [True, True, False]
    assert [b.tolist() for b in box.bounds] == [[0, 0, 0], [2, 1, 1]]

    sphere = Sphere([0, 0, 0], 1)
    assert _inside(sphere, [1, 0, 0], [0.6, 0.6, 0.6]) == [True, False]
    assert [b.tolist() for b in sphere.bounds] == [[-1, -1, -1], [1, 1, 1]]

    ellipsoid = Ellipsoid([0, 0, 0], [2, 1, 1])
    assert _inside(ellipsoid, [1.9, 0, 0], [0, 1.1, 0]) == [True, False]

    cylinder = Cylinder([0, 0, 0], [10, 0, 0], 1)  # along x
    assert _inside(cylinder, [5, 0.9, 0], [5, 0.7, 0.7], [-0.1, 0, 0], [10, 0, 1]) == [True, True, False, True]
    assert [b.tolist() for b in cylinder.bounds] == [[0, -1, -1], [10, 1, 1]]

    cone = Cone([0, 0, 0], [0, 0, 10], 2, 0)
    assert _inside(cone, [1.9, 0, 0], [1.9, 0, 5], [0.9, 0, 5]) == [True, False, True]

    triangle = Polygon([[0, 0], [4, 0], [0, 4]], z=[0, 1])
    assert _inside(triangle, [1, 1, 0.5], [3, 3, 0.5], [1, 1, 2]) == [True, False, False]
    assert np.isinf(Polygon([[0, 0], [1, 0], [0, 1]]).bounds[0][2])


def test_shape_operations():
    plate = Box([0, 0, 0], [10, 10, 0])
    hole = Cylinder([5, 5, -1], [5, 5, 1], 2)
    assert _inside(plate - hole, [5, 5, 0], [1, 1, 0]) == [False, True]
    assert _inside(plate + Sphere([20, 0, 0], 1), [20, 0, 0]) == [True]
    assert _inside(plate & Box([0, 0, 0], [5, 5, 0]), [4, 4, 0], [6, 6, 0]) == [True, False]
    assert [b.tolist() for b in (plate + Sphere([20, 0, 0], 1)).bounds] == [[0, -1, -1], [21, 10, 1]]


# --- expressions -------------------------------------------------------------------------------


def test_expressions_evaluate_on_arrays():
    x = np.array([0.0, 1.0, 2.0])
    names = {"L": 2.0, "x": x}
    assert evaluate("L / 2 + 2 ** 3", names) == 9
    assert evaluate("0 < x <= L and not x == 1", names).tolist() == [False, False, True]
    assert evaluate("x < 1 or x > 1.5", names).tolist() == [True, False, True]
    assert evaluate("int(5 / 2) + sqrt(4) + abs(-1) + max(1, 2)", {}) == 7
    assert evaluate("sin(pi / 2)", {}) == pytest.approx(1)
    assert evaluate(3.5, {}) == 3.5


@pytest.mark.parametrize(
    "expression",
    ["__import__('os')", "x.__class__", "x[0]", "(lambda: 1)()", "open('f')", "LENGHT", "print(1)", "1 if x else 2"],
)
def test_expressions_reject_everything_else(expression):
    with pytest.raises(ExpressionError):
        evaluate(expression, {"x": np.zeros(2)})


# --- YAML models -------------------------------------------------------------------------------

PLATE = """
title: Plate
parameters:
  DISCRETIZATION: {default: 10, label: Points}
  LENGTH: 10
  HEIGHT: {default: 4}
  HOLE: {default: true}
geometry:
  spacing: HEIGHT / DISCRETIZATION
  add:
    - box: {min: [0, 0, -1], max: [LENGTH, HEIGHT, 1]}
  remove:
    - if: HOLE
      cylinder: {start: [LENGTH / 2, HEIGHT / 2, -2], end: [LENGTH / 2, HEIGHT / 2, 2], radius: 1}
blocks:
  - {id: 2, where: "x < spacing"}
  - {id: 3, box: {min: [LENGTH - 1, 0, -1], max: [LENGTH, HEIGHT, 1]}}
set:
  solvers[0].finalTime: LENGTH / 1000
"""


def test_yaml_model_builds_points_blocks_and_shapes():
    Model = model_class(PLATE, "Plate")
    assert [p.name for p in Model.params()] == ["DISCRETIZATION", "LENGTH", "HEIGHT", "HOLE"]
    assert Model.params()[1].valve()["type"] == "number"
    assert Model.params()[3].valve()["type"] == "checkbox"

    data = _data()
    result = Model({}, data).build()
    assert data.solvers[0].finalTime == pytest.approx(0.01)
    x, y, block = result["x"], result["y"], result["block"]
    assert result["dx"][0] == pytest.approx(0.4)
    assert x.min() == 0 and x.max() == pytest.approx(10) and y.max() == pytest.approx(4)
    assert not np.any((x - 5) ** 2 + (y - 2) ** 2 < 0.99), "hole removed"
    assert set(block[x < 0.4]) == {2} and set(block[x >= 9]) == {3}
    assert [(s["role"], s["type"]) for s in result["shapes"]] == [
        ("add", "box"),
        ("remove", "cylinder"),
        ("block", "box"),
    ]
    block3 = next(b for b in result["blocks"] if b["id"] == 3)
    assert block3["bounds"] == {"minX": 9, "maxX": 10, "minY": 0, "maxY": 4}

    without_hole = Model({"HOLE": False}, _data()).build()
    assert len(without_hole["x"]) > len(x)
    assert len(Model({}, _data(two_d=False)).build()["x"]) == len(x) * 6  # z = -1 .. 1 in 0.4 steps


@pytest.mark.parametrize(
    "change, message",
    [
        (("HEIGHT / DISCRETIZATION", "HEIGTH / DISCRETIZATION"), "geometry.spacing: unknown name 'HEIGTH'"),
        (("radius: 1}", "radius: 1, colour: 2}"), "geometry.remove[0].cylinder: wrong arguments"),
        (('where: "x < spacing"', 'where: "x.real"'), "blocks[0].where: 'x.real' is not allowed"),
        (("- {id: 2, ", "- {"), "blocks[0]: every block needs an 'id'"),
        (("title: Plate", "title: Plate\nmesh: 1"), "mesh: unknown section"),
        (("  LENGTH: 10", "  LENGTH: {label: L}"), "parameters.LENGTH: missing 'default'"),
        (("solvers[0].finalTime", "nosuch.field"), "set.nosuch.field: no such input-deck field"),
        (("add:", "add: [\n"), "line "),
    ],
)
def test_yaml_errors_name_their_path(change, message):
    text = PLATE.replace(*change)
    with pytest.raises(ModelSpecError) as error:
        model_class(text, "Plate")({}, _data()).build()
    assert message in str(error.value)


def test_spacing_defaults_to_shortest_edge_over_odd_count():
    text = PLATE.replace("  spacing: HEIGHT / DISCRETIZATION\n", "")
    assert model_class(text)({}, _data()).spacing == pytest.approx(4 / 11)


# --- loader ------------------------------------------------------------------------------------


@pytest.fixture
def own_models(tmp_path, monkeypatch):
    monkeypatch.setitem(loader.MODEL_DIRS, "own", tmp_path)
    return tmp_path


def _write(folder, name, text):
    folder.mkdir(exist_ok=True)
    (folder / name).write_text(textwrap.dedent(text), encoding="utf-8")


def test_loader_python_model_metadata_and_analyses(own_models):
    _write(
        own_models / "Beam",
        "Beam.py",
        """
        from perihub import Param, PeriHubModel, analysis, box

        class Model(PeriHubModel):
            title = "Beam"
            requirements = ["crackpy"]
            LENGTH = Param(4.0, "Length")
            spacing = 1.0

            def geometry(self):
                return box([0, 0, 0], [self.LENGTH, 1, 0])

        @analysis("Energy", STEP=Param(1, "Step"))
        def energy(ctx):
            return ctx.STEP
        """,
    )
    assert len(loader.load_model("Beam")({"LENGTH": 2}, _data()).build()["x"]) == 6
    assert [a for a in loader.load_analyses("Beam")] == ["energy"]
    info = next(m for m in loader.list_models("own") if m["file"] == "Beam")
    assert (info["title"], info["requirements"], info["format"]) == ("Beam", "crackpy", "python")


def test_loader_yaml_analysis_file(own_models):
    _write(own_models / "Plate", "Plate.yaml", PLATE)
    assert loader.load_analyses("Plate") == {}
    _write(
        own_models / "Plate",
        "analysis.py",
        """
        from perihub import analysis

        @analysis("Curve")
        def curve(ctx):
            return None
        """,
    )
    assert list(loader.load_analyses("Plate")) == ["curve"]


def test_loader_reports_legacy_models(own_models):
    _write(own_models / "Old", "Old.py", "class Valves:\n    pass\n\nclass main:\n    pass\n")
    with pytest.raises(LookupError, match="legacy model format"):
        loader.load_model("Old")
    info = next(m for m in loader.list_models("own") if m["file"] == "Old")
    assert "legacy model format" in info["error"]


def test_built_in_models_win_and_bad_names_are_rejected(own_models):
    _write(own_models / "Dogbone", "Dogbone.yaml", PLATE)
    assert loader.find_model("Dogbone")[0].parent.parent == loader.MODEL_DIRS["built_in"]
    for name in ("../models/Dogbone", ".hidden", ""):
        with pytest.raises(LookupError):
            loader.find_model(name)


def test_block_labels_sit_deep_inside_their_block():
    text = (loader.APP_DIR / "assets" / "model_template.yaml").read_text().replace("{title}", "T")
    result = model_class(text)({}, _data()).build()
    labels = {b["id"]: (b["labelX"], b["labelY"]) for b in result["blocks"]}
    # Block 1 surrounds the hole (radius 2 at 10, 5); its label must not sit on the hole's edge.
    x, y = labels[1]
    assert ((x - 10) ** 2 + (y - 5) ** 2) ** 0.5 > 2 + 2 * result["dx"][0]
    # The thin end blocks are labelled in their middle, not at a corner.
    assert labels[2][1] == pytest.approx(5, abs=result["dx"][0])
    assert model_class(text)({}, _data()).build(summary=False)["blocks"] == []
