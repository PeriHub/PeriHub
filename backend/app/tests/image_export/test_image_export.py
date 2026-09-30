# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import results

client = TestClient(app)

FIXTURE = os.path.join(os.path.dirname(__file__), "Dogbone_Output1.e")


@pytest.fixture
def result_folder(tmp_path, monkeypatch):
    """A run folder in tmp_path. Finding the run (DB + local PeriLab) is bypassed, so the tests never touch the
    real simulations volume."""
    monkeypatch.setattr(results, "_result_folder", lambda *args: str(tmp_path))
    return tmp_path


def test_getPointData(result_folder):
    shutil.copy(FIXTURE, result_folder / "Dogbone_Output1.e")
    response = client.get("/results/points")
    assert response.status_code == 200, response.text
    assert response.json()["number_of_steps"] == 49


def test_getPlot(result_folder):
    (result_folder / "Dogbone_Output1.csv").write_text("Time,Force\n0.0,1.5\n1.0,2.5\n")
    response = client.get(
        "/results/plot", params={"model_name": "Dogbone", "model_folder_name": "Default", "output": "Output1"}
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"Time": [0.0, 1.0], "Force": [1.5, 2.5]}
