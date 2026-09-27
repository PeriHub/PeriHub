# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import copy
from types import SimpleNamespace

from backend.app.support.base_models import ModelData, default_model
from backend.app.support.writer.yaml_writer_perilab import YAMLcreatorPeriLab

THERMAL = {"name": "T1", "thermalModel": ["Thermal Flow"], "thermalType": "Bond based"}
ADDITIVE = {"name": "A1", "additiveType": "Simple", "printTemp": 200}


def _writer(model_data):
    model_writer = SimpleNamespace(filename="m", ns_name="ns", node_set_ids=[], model_data=model_data)
    return YAMLcreatorPeriLab(model_writer, block_def=model_data.blocks)


def test_thermal_and_additive_written_only_when_referenced_by_a_block():
    data = copy.deepcopy(default_model)
    data["thermal"], data["additive"] = [THERMAL], [ADDITIVE]
    model_data = ModelData(**data)

    assert _writer(model_data).thermal() == {}
    assert _writer(model_data).additive() == {}

    model_data.blocks[0].thermalModel = "T1"
    model_data.blocks[0].additiveModel = "A1"
    assert list(_writer(model_data).thermal()) == ["T1"]
    assert list(_writer(model_data).additive()) == ["A1"]


def test_legacy_enabled_sections_are_unwrapped():
    data = copy.deepcopy(default_model)
    data["thermal"] = {"enabled": False, "thermalModels": [THERMAL]}
    data["additive"] = {"enabled": True, "additiveModels": [ADDITIVE]}
    data["contact"] = {"enabled": False, "contactModels": [{}]}
    model_data = ModelData(**data)

    assert model_data.thermal == []
    assert [a.name for a in model_data.additive] == ["A1"]
    assert model_data.contact.contactModels == []
