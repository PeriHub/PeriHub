# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""ModelData holds PeriLab keys in `params`; old camelCase configs are rejected, not silently emptied."""

import copy

import pytest
from pydantic import ValidationError

from backend.app.support.base_models import ModelData, default_model


def test_default_model_validates_and_keeps_params():
    data = ModelData(**copy.deepcopy(default_model))
    assert data.materials[0].params["Young's Modulus"] == 200000.0
    assert data.solvers[0].solverOptions["Safety Factor"] == 0.95
    assert data.blocks[0].params["Material Model"] == "Aluminium"


@pytest.mark.parametrize(
    "section, change",
    [
        ("materials", {"youngsModulus": 1.0}),
        ("blocks", {"density": 1.0}),
        ("solvers", {"finalTime": 1.0}),
        ("outputs", {"numberOfOutputSteps": 10}),
        ("bondFilters", {"lowerLeftCornerX": 0.0}),
    ],
)
def test_old_camel_case_fields_are_rejected(section, change):
    data = copy.deepcopy(default_model)
    data[section][0].update(change)
    with pytest.raises(ValidationError):
        ModelData(**data)


def test_pre_calculations_are_gone():
    data = copy.deepcopy(default_model)
    data["preCalculations"] = None
    with pytest.raises(ValidationError):
        ModelData(**data)
