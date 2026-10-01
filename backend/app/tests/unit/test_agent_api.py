# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""The endpoints a spec-only workflow agent uses (see /openapi.agent.json)."""

import glob
import json
import os
import shutil

import pytest

from backend.app.db import base
from backend.app.main import app
from backend.app.routers import jobs, results
from backend.app.support import job_queue
from backend.app.support.base_models import ModelData
from backend.app.support.model import loader
from backend.app.support.results import summary

from .test_guest import _auth, _dogbone, _FakeBackend, _generate, _job, _signup, isolated  # noqa: F401 - fixture

EXODUS_FIXTURE = os.path.join(os.path.dirname(__file__), "..", "image_export", "Dogbone_Output1.e")


@pytest.fixture
def backend(monkeypatch):
    fake = _FakeBackend()
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: fake)
    monkeypatch.setattr(jobs, "get_solver_backend", lambda: fake)
    return fake


def _run(user, job_id="p-1"):
    with base.SessionLocal() as db:
        return _job(db, user["user_id"], 1, job_id)


def test_get_run_returns_live_status(client, backend):
    owner = _signup(client, "a@x.de")
    run_id = _run(owner)

    r = client.get(f"/jobs/{run_id}", headers=_auth(owner))
    assert r.status_code == 200, r.text
    assert r.json()["id"] == run_id
    assert r.json()["status"] == "running"

    backend.client().status = "completed"  # PeriLab finished -> synced to the DB status "done"
    assert client.get(f"/jobs/{run_id}", headers=_auth(owner)).json()["status"] == "done"


def test_get_run_hides_other_users_runs(client, backend):
    owner = _signup(client, "a@x.de")  # first signup is the admin
    other = _signup(client, "b@x.de")
    run_id = _run(owner)

    assert client.get(f"/jobs/{run_id}", headers=_auth(other)).status_code == 403
    assert client.get("/jobs/unknown", headers=_auth(owner)).status_code == 404
    assert client.get(f"/jobs/{run_id}").status_code == 401


def test_get_run_log_tails_and_filters_debug(client, backend):
    owner = _signup(client, "a@x.de")
    run_id = _run(owner)
    backend.client().log = "step 1\n[Debug] noise\nstep 2\n"

    r = client.get(f"/jobs/{run_id}/log?tail=50", headers=_auth(owner))
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/plain")
    assert r.text == "step 1\nstep 2\n"
    assert backend.client().log_requests == [("p-1", 50)]

    r = client.get(f"/jobs/{run_id}/log?debug=true", headers=_auth(owner))
    assert r.text == "step 1\n[Debug] noise\nstep 2\n"


def test_get_run_log_404_before_perilab_job(client, backend):
    owner = _signup(client, "a@x.de")
    run_id = _run(owner, job_id=None)
    assert client.get(f"/jobs/{run_id}/log", headers=_auth(owner)).status_code == 404


def _operations(spec):
    return {op["operationId"]: op for path in spec["paths"].values() for op in path.values()}


def test_workflow_responses_are_typed():
    ops = _operations(app.openapi())
    for name in ["generate_model", "get_config", "run_model", "cancel_run", "delete_run", "get_plot", "get_run"]:
        assert ops[name]["responses"]["200"]["content"]["application/json"]["schema"] != {}, name
    run_status = app.openapi()["components"]["schemas"]["RunStatus"]["properties"]["status"]
    assert run_status["enum"] == ["queued", "running", "done", "failed", "cancelled"]


@pytest.mark.parametrize("path", sorted(glob.glob("./models/*/*.json")))
def test_builtin_configs_match_model_data(path):
    with open(path, encoding="UTF-8") as file:
        ModelData.model_validate(json.load(file))


def test_generate_reports_nodes_and_blocks(client, isolated):  # noqa: F811
    user = _signup(client, "a@x.de")
    r = _generate(client, _auth(user), _dogbone())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["model_name"] == "Dogbone" and body["model_folder_name"] == "Default"
    assert body["nodes"] > 0
    assert body["blocks"] == len(_dogbone()["blocks"])


def test_exodus_summary_uses_last_written_step():
    s = summary.exodus_summary(EXODUS_FIXTURE, "Output1")
    assert s.name == "Output1"
    assert s.last_step == 46
    assert s.final_time == pytest.approx(5.044955e-06, rel=1e-5)
    assert {"Displacementsx", "Displacementsy", "Damage", "von Mises Stress"} <= set(s.variables)
    # vectors also get their magnitude under the base name; tensor rows don't
    assert s.variables["Displacements"].max > 0
    assert s.variables["Displacements"].max >= s.variables["Displacementsx"].max
    assert "Cauchy Stressx" not in s.variables
    assert set(s.globals) == {
        "External_Displacementsx",
        "External_Displacementsy",
        "External_Forcesx",
        "External_Forcesy",
    }


def test_csv_summary_skips_non_numeric_columns(tmp_path):
    path = tmp_path / "Dogbone_Output2.csv"
    path.write_text("Time,Force,Label\n0,0,a\n1,5,b\n2,3,c\n", encoding="utf-8")
    columns = summary.csv_summary(str(path))
    assert set(columns) == {"Time", "Force"}
    assert columns["Force"].model_dump() == {"final": 3.0, "min": 0.0, "max": 5.0}


def test_get_run_summary(client, backend, monkeypatch, tmp_path):
    shutil.copy(EXODUS_FIXTURE, tmp_path / "Dogbone_Output1.e")
    (tmp_path / "Dogbone_Output2.csv").write_text("Time,Force\n0,0\n1,5\n", encoding="utf-8")
    monkeypatch.setattr(results, "_result_folder", lambda *_: str(tmp_path))
    owner = _signup(client, "a@x.de")
    run_id = _run(owner)

    r = client.get(f"/results/summary?run_id={run_id}", headers=_auth(owner))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["run_id"] == run_id and body["status"] == "running"
    assert [o["name"] for o in body["outputs"]] == ["Output1"]
    assert body["csv"]["Output2"]["Force"] == {"final": 5.0, "min": 0.0, "max": 5.0}
    assert body["analyses"] == list(loader.load_analyses("Dogbone"))


def test_auth_schemes_are_declared():
    spec = app.openapi()
    assert set(spec["components"]["securitySchemes"]) == {"APIKeyHeader", "HTTPBearer"}
    assert spec["components"]["securitySchemes"]["APIKeyHeader"]["name"] == "X-Api-Key"
    assert {"APIKeyHeader": []} in _operations(spec)["run_model"]["security"]
