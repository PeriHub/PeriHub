"""The endpoints a spec-only workflow agent uses (see /openapi.agent.json)."""

import glob
import json
import os
import shutil

import pytest
from fastapi.testclient import TestClient

from backend.app.db import base
from backend.app.main import AGENT_OPERATIONS, app
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
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda *_: fake)
    monkeypatch.setattr(jobs, "get_solver_backend", lambda *_: fake)
    return fake


def _run(user, job_id="p-1"):
    with base.SessionLocal() as db:
        return _job(db, user["user_id"], 1, job_id)


def test_get_run_returns_live_status(client, backend):
    owner = _signup(client, "a@x.de")
    run_id = _run(owner)

    r = client.get(f"/jobs/{run_id}", headers=_auth(owner))
    assert r.status_code == 200, r.text
    assert r.json()["id"] == r.json()["run_id"] == run_id
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
    for name in [
        "generate_perihub_model",
        "get_perihub_model_config",
        "run_perihub_simulation",
        "cancel_perihub_run",
        "delete_run",
        "get_plot",
        "get_perihub_run",
    ]:
        assert ops[name]["responses"]["200"]["content"]["application/json"]["schema"] != {}, name
    run_status = app.openapi()["components"]["schemas"]["RunStatus"]["properties"]["status"]
    assert run_status["enum"] == ["queued", "running", "done", "failed", "cancelled"]
    # one ModelData schema for request and response, not ModelData-Input/-Output (the frontend imports ModelData)
    assert "ModelData" in app.openapi()["components"]["schemas"]


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
    assert body["files"] == ["Dogbone_Output1.e", "Dogbone_Output2.csv"]


def test_get_result_file(client, backend, monkeypatch, tmp_path):
    shutil.copy(EXODUS_FIXTURE, tmp_path / "Dogbone_Output1.e")
    monkeypatch.setattr(results, "_result_folder", lambda *_: str(tmp_path))
    owner = _signup(client, "a@x.de")
    run_id = _run(owner)

    r = client.get(f"/results/{run_id}/files/Dogbone_Output1.e", headers=_auth(owner))
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.content == open(EXODUS_FIXTURE, "rb").read()
    assert client.get(f"/results/{run_id}/files/missing.e", headers=_auth(owner)).status_code == 404
    assert client.get(f"/results/{run_id}/files/..", headers=_auth(owner)).status_code in (400, 404)


def test_generate_and_run_without_body(client, isolated, monkeypatch):  # noqa: F811
    submitted = []

    def fake_submit(db, user, model_name, model_folder_name, remotepath, **kwargs):
        submitted.append((model_name, model_folder_name, kwargs["num_procs"]))
        return type("Entry", (), {"id": "r-1", "perilab_job_id": "p-1"})

    monkeypatch.setattr(jobs, "submit_job", fake_submit)
    headers = _auth(_signup(client, "a@x.de"))
    run = "/jobs?model_name=Dogbone&model_folder_name=Default"
    assert client.post(run, headers=headers).status_code == 404  # nothing generated yet

    r = client.post("/workspaces/Dogbone/Default/generate", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["nodes"] > 0

    r = client.post(run, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["run_id"] == "r-1"
    assert submitted == [("Dogbone", "Default", 1)]  # job.tasks from the saved ModelData


def test_model_list_is_typed(client):
    models = client.get("/models").json()
    assert {"name": "Dogbone", "file": "Dogbone"}.items() <= next(m for m in models if m["name"] == "Dogbone").items()
    item = app.openapi()["paths"]["/models"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert item["items"] == {"$ref": "#/components/schemas/ModelInfo"}


def test_auth_schemes_are_declared():
    spec = app.openapi()
    assert set(spec["components"]["securitySchemes"]) == {"APIKeyHeader", "HTTPBearer"}
    assert spec["components"]["securitySchemes"]["APIKeyHeader"]["name"] == "X-Api-Key"
    assert {"APIKeyHeader": []} in _operations(spec)["run_perihub_simulation"]["security"]


def test_agent_operations_exist():
    assert AGENT_OPERATIONS <= set(_operations(app.openapi()))


def test_agent_spec_is_the_typed_workflow_subset():
    spec = TestClient(app).get("/openapi.agent.json").json()
    ops = _operations(spec)
    assert set(ops) == AGENT_OPERATIONS
    assert spec["servers"] == [{"url": "."}]
    assert "get_perihub_run_summary" in spec["info"]["description"]
    assert spec["components"]["securitySchemes"]
    for name, op in ops.items():
        assert op.get("description"), name
        for code, response in op["responses"].items():
            if code.startswith("2") and "application/json" in response.get("content", {}):
                assert response["content"]["application/json"]["schema"] != {}, name
    # LAS vendor extensions survive the filter: only run_perihub_simulation is a long-running job
    run = spec["paths"]["/jobs"]["post"]
    assert run["x-las-async"] is True and run["x-las-job-id-field"] == "run_id"
    assert run["x-las-status-path"] == "/jobs/{jobId}"
    assert run["x-las-result-path"] == "/results/summary?run_id={jobId}"
    assert run["x-las-poll-interval-ms"] == 15000
    sync = {
        "get_perihub_run",
        "get_perihub_run_log",
        "list_perihub_runs",
        "cancel_perihub_run",
        "get_perihub_run_summary",
        "render_perihub_analysis",
        "list_perihub_model_analyses",
        "get_perihub_result_file",
    }
    assert {name for name, op in ops.items() if op.get("x-las-async") is False} == sync
    # the full spec is untouched
    assert "servers" not in app.openapi()
    assert "/openapi.agent.json" not in app.openapi()["paths"]
