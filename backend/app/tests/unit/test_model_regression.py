# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""The built-in models were converted from the old Valves/main generators to YAML/PeriHubModel.
Fixtures hold the old generators' output (points, blocks, edited bond filters). The converted
models must reproduce it — except that the old grids (np.arange(start, end + dx, dx)) overshot
the specified body by up to one row; those points lie outside the nominal geometry and are
intentionally gone."""

import glob
import json
import os

import numpy as np
import pytest

from backend.app.support.base_models import ModelData
from backend.app.support.model import loader

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "model_regression")
CASES = sorted(os.path.basename(f)[: -len(".npz")] for f in glob.glob(os.path.join(FIXTURES, "*.npz")))


def _lattice_keys(x, y, z, dx):
    return [tuple(p) for p in np.round(np.c_[x, y, z] / dx, 4)]


@pytest.mark.parametrize("case", CASES)
def test_converted_model_matches_old_generator(case):
    name, tag = case.rsplit("_", 1)
    old = np.load(os.path.join(FIXTURES, case + ".npz"))
    valves = json.loads(str(old["valves"]))
    dx = float(old["dx"])

    with open(loader.find_model(name)[0].parent / (name + ".json"), encoding="UTF-8") as file:
        data = ModelData(**json.load(file))
    data.model.twoDimensional = tag == "2d"
    model = loader.load_model(name)(valves, data)
    new = model.build()

    assert new["dx"][0] == pytest.approx(dx)
    old_points = dict(zip(_lattice_keys(old["x"], old["y"], old["z"], dx), old["block"].tolist()))
    new_points = dict(zip(_lattice_keys(new["x"], new["y"], new["z"], dx), new["block"].tolist()))

    assert new_points.keys() <= old_points.keys(), "the converted model creates points the old one didn't"
    assert {p: old_points[p] for p in new_points} == new_points, "block ids differ"

    dropped = np.array([p for p in old_points if p not in new_points]).reshape(-1, 3) * dx
    if len(dropped):
        lo, hi = model.geometry().bounds
        outside = np.any((dropped > hi + 1e-9) | (dropped < lo - 1e-9), axis=1)
        assert outside.all(), "points inside the nominal body went missing"

    bond_filters = [[b.lowerLeftCornerX, b.lowerLeftCornerY, b.bottomLength] for b in data.bondFilters or []]
    np.testing.assert_allclose(
        np.array(bond_filters, dtype=float), np.array(json.loads(str(old["bond_filters"])), dtype=float)
    )
