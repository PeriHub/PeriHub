import copy
from types import SimpleNamespace

from backend.app.support.base_models import ModelData, default_model
from backend.app.support.writer.yaml_writer_perilab import YAMLcreatorPeriLab

THERMAL = {"name": "T1", "params": {"Thermal Model": "Thermal Flow", "Type": "Bond based"}}
ADDITIVE = {"name": "A1", "params": {"Additive Model": "Simple"}}


def _writer(model_data):
    model_writer = SimpleNamespace(filename="m", ns_name="ns", node_set_ids=[], model_data=model_data)
    return YAMLcreatorPeriLab(model_writer, block_def=model_data.blocks)


def test_thermal_and_additive_written_only_when_referenced_by_a_block():
    data = copy.deepcopy(default_model)
    data["thermal"], data["additive"] = [THERMAL], [ADDITIVE]
    model_data = ModelData(**data)

    assert _writer(model_data).thermal() == {}
    assert _writer(model_data).additive() == {}

    model_data.blocks[0].params.update({"Thermal Model": "T1", "Additive Model": "A1"})
    assert list(_writer(model_data).thermal()) == ["T1"]
    assert list(_writer(model_data).additive()) == ["A1"]
