"""The writer merges each entry's `params` with the keys PeriHub derives; derived keys win."""

import copy
from types import SimpleNamespace

import numpy as np
import pytest
import yaml
from fastapi import HTTPException

from backend.app.support.base_models import ModelData, default_model
from backend.app.support.writer.model_writer import _validate_deviation_path
from backend.app.support.writer.yaml_writer_perilab import YAMLcreatorPeriLab


def _data(**changes):
    data = copy.deepcopy(default_model)
    data.update(changes)
    return ModelData(**data)


def _writer(model_data, node_set_ids=(2, 3)):
    model_writer = SimpleNamespace(filename="m", ns_name="ns", node_set_ids=list(node_set_ids), model_data=model_data)
    return YAMLcreatorPeriLab(model_writer, block_def=model_data.blocks)


def test_params_are_written_verbatim_and_unset_values_dropped():
    data = _data()
    data.materials[0].params.update({"Accuracy Order": 2, "Bulk Modulus": None, "Linear Strain": ""})
    material = _writer(data).materials()["BC"]
    assert material["Accuracy Order"] == 2
    assert material["Young's Modulus"] == 200000.0
    assert "Bulk Modulus" not in material and "Linear Strain" not in material


def test_derived_keys_win_over_params():
    data = _data()
    data.blocks[0].params["Block ID"] = 99
    data.outputs[0].params["Output Filename"] = "hacked"
    writer = _writer(data)
    assert writer.blocks(99)["Part"]["Block ID"] == 1
    assert writer.output()["Output1"]["Output Filename"] == "m_Output1"


def test_user_material_properties():
    data = _data()
    data.materials[0].properties = [{"name": "Prop_1", "value": 1.5}, {"name": "Prop_2", "value": 2.0}]
    material = _writer(data).materials()["BC"]
    assert material["Number of Properties"] == 2
    assert material["Prop_1"] == 1.5 and material["Prop_2"] == 2.0


def test_interblock_damage_only_with_existing_blocks():
    data = _data()
    data.damages[0].interBlocks = [{"firstBlockId": 1, "secondBlockId": 2, "value": 0.1}]
    assert _writer(data).damage(5)["Damage"]["Interblock Damage"] == {"Interblock Critical Value 1_2": 0.1}
    assert "Interblock Damage" not in _writer(data).damage(1)["Damage"]


def test_solver_sub_section_and_multistep():
    data = _data()
    writer = _writer(data)
    solver = writer.solver(data.solvers[0])
    assert solver["Final Time"] == 0.0005
    assert solver["Verlet"] == {"Safety Factor": 0.95, "Numerical Damping": 5e-06}
    assert "Step ID" not in solver

    data.solvers.append(data.solvers[0].model_copy(update={"stepId": 2, "name": "Step 2", "solvertype": "Static"}))
    data.solvers[0].name = "Step 1"
    steps = _writer(data).multistep_solver()
    assert steps["Step 2"]["Step ID"] == 2 and "Static" in steps["Step 2"]


def test_boundary_condition_node_sets_and_steps():
    data = _data()
    bcs = _writer(data).boundary_conditions(multistep=True)
    assert bcs["BC_1"]["Node Set"] == "Node Set 1"  # blockId 2 is the first node set id
    assert bcs["BC_2"]["Node Set"] == "Node Set 2"
    assert bcs["BC_1"]["Step ID"] == "1"
    assert bcs["BC_1"]["Value"] == "1000*t"
    data.boundaryConditions.conditions[0].nodeSet = 7
    assert _writer(data).boundary_conditions(False)["BC_1"]["Node Set"] == "Node Set 7"


def test_discretization_mesh_node_sets_and_bond_filters():
    data = _data()
    disc = _writer(data).discretization()
    assert disc["Type"] == "Text File" and disc["Input Mesh File"] == "m.txt"
    assert disc["Node Sets"] == {"Node Set 1": "ns_1.txt", "Node Set 2": "ns_2.txt"}
    assert disc["Distribution Type"] == "Neighbor based"
    assert disc["Bond Filters"]["bf_1"]["Bottom Length"] == 56.75


def test_outputs_list_variables_and_computes():
    data = _data()
    out = _writer(data).output()
    assert out["Output1"]["Output Variables"]["Displacements"] is True
    assert out["Output1"]["Output Variables"]["External_Force"] is True
    assert out["Output1"]["Number of Output Steps"] == 100


def test_contact_globals_and_groups():
    data = _data(
        contact={
            "params": {"Global Search Frequency": 10},
            "contactModels": [
                {
                    "name": "C1",
                    "params": {"Type": "Penalty Contact", "Contact Radius": 0.1},
                    "contactGroups": [{"name": "G1", "params": {"Master Block ID": 1, "Slave Block ID": 2}}],
                }
            ],
        }
    )
    contact = _writer(data).contact()
    assert contact["Globals"] == {"Global Search Frequency": 10}
    assert contact["C1"]["Contact Groups"] == {"G1": {"Master Block ID": 1, "Slave Block ID": 2}}


def test_full_deck_is_yaml():
    deck = yaml.safe_load(_writer(_data()).create_yaml(5))["PeriLab"]
    assert set(deck) >= {"Discretization", "Models", "Blocks", "Solver", "Boundary Conditions", "Outputs"}
    assert deck["Compute Class Parameters"]["External_Force"]["Block"] == "Bottom_BC"


def test_numpy_scalar_in_params_is_written_as_plain_float():
    """A numpy.float64 (e.g. a generated Horizon) must not make yaml.dump emit a `!!python/object` tag -
    deck_guard.py's safe_load can't read that back, so submission would fail with a cryptic 422."""
    data = _data()
    data.materials[0].params["Young's Modulus"] = np.float64(200000.0)
    yaml_text = _writer(data).create_yaml(5)
    deck = yaml.safe_load(yaml_text)  # raises if a !!python/object tag slipped through
    value = deck["PeriLab"]["Models"]["Material Models"]["BC"]["Young's Modulus"]
    assert value == 200000.0 and type(value) is float


def test_deviation_path_accepts_plain_field_paths():
    assert _validate_deviation_path('materials[0].params["Young\'s Modulus"]')


def test_deviation_path_rejects_dunder_access():
    with pytest.raises(HTTPException) as exc:
        _validate_deviation_path("__class__.__init__")
    assert exc.value.status_code == 422
