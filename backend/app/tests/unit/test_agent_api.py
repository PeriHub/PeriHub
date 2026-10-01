# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""The endpoints a spec-only workflow agent uses (see /openapi.agent.json)."""

import pytest

from backend.app.db import base
from backend.app.routers import jobs
from backend.app.support import job_queue

from .test_guest import _auth, _FakeBackend, _job, _signup


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
