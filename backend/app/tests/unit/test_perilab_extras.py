# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""`extra` / `solverOptions`: PeriLab keys PeriHub has no own field for, merged into the deck; native keys win."""

import copy
from types import SimpleNamespace

from backend.app.support.base_models import ModelData, default_model
from backend.app.support.writer.yaml_writer_perilab import YAMLcreatorPeriLab


def _writer(model_data):
    model_writer = SimpleNamespace(filename="m", ns_name="ns", node_set_ids=[1, 2, 3], model_data=model_data)
    return YAMLcreatorPeriLab(model_writer, block_def=model_data.blocks)


def _model(**changes):
    data = copy.deepcopy(default_model)
    data.update(changes)
    return ModelData(**data)


def test_extra_defaults_to_empty():
    model_data = _model()
    assert model_data.materials[0].extra == {}
    assert model_data.solvers[0].solverOptions == {}


def test_material_extra_is_merged_and_native_keys_win():
    model_data = _model()
    material = model_data.materials[0]
    material.extra = {"Accuracy Order": 2, "Material Model": "Hacked"}
    written = _writer(model_data).materials()[material.name]
    assert written["Accuracy Order"] == 2
    assert written["Material Model"] != "Hacked"


def test_extra_is_merged_into_every_section():
    model_data = _model()
    model_data.blocks[0].extra = {"Angle X": 1.0}
    model_data.outputs[0].extra = {"Flush File": False}
    model_data.boundaryConditions.conditions[0].extra = {"Coordinate": "native wins"}
    model_data.discretization.extra = {"Horizon Mesh Scaling X": 1.5}
    model_data.damages[0].extra = {"Local Damping": 0.1}
    writer = _writer(model_data)
    assert writer.blocks(99)[model_data.blocks[0].name]["Angle X"] == 1.0
    assert writer.output()["Output1"]["Flush File"] is False
    assert writer.create_boundary_conditions(False)["BC_1"]["Coordinate"] == "y"
    assert writer.load_mesh()["Horizon Mesh Scaling X"] == 1.5
    assert writer.damage(99)[model_data.damages[0].name]["Local Damping"] == 0.1


def test_damage_model_without_native_branch_takes_critical_value_from_extra():
    model_data = _model()
    damage = model_data.damages[0]
    damage.damageModel = "Critical Energy Anisotropic"
    damage.extra = {"Critical Value": 5.0}
    assert _writer(model_data).damage(99)[damage.name]["Critical Value"] == 5.0


def test_solver_extra_and_verlet_options():
    model_data = _model()
    solver = model_data.solvers[0]
    solver.solvertype = "Verlet"
    solver.extra = {"Degradation Models": True, "Final Time": -1}
    solver.solverOptions = {"Fixed dt": 1e-7, "Safety Factor": 99}  # default_model: fixedDt None, safetyFactor 0.95
    written = _writer(model_data).solver()
    assert written["Degradation Models"] is True
    assert written["Final Time"] == 0.0005
    assert written["Verlet"]["Safety Factor"] == 0.95
    assert written["Verlet"]["Fixed dt"] == 1e-7


def test_solver_type_without_native_branch_writes_its_options():
    model_data = _model()
    solver = model_data.solvers[0]
    solver.solvertype = "Newmark"
    solver.solverOptions = {"Newmark Alpha": 0.25}
    written = _writer(model_data).solver()
    assert written["Newmark"] == {"Newmark Alpha": 0.25}
    assert "Verlet" not in written and "Static" not in written
