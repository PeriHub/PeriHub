# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.db import base
from backend.app.db.models import JOB_CANCELLED, JOB_DONE, JOB_RUNNING, JobQueueEntry, User
from backend.app.routers import jobs
from backend.app.support import guest_sweeper, job_queue
from backend.app.support.base_models import ModelData
from backend.app.support.file_handler import FileHandler
from backend.app.support.guest import apply_guest_limits
from backend.app.support.perilab_api_client import PeriLabJob

from .conftest import set_instance_setting


def _signup(client, email):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    return r.json()


def _auth(body):
    return {"Authorization": f"Bearer {body['token']}"}


def test_public_config_reports_guest_access(client):
    config = client.get("/config/public").json()
    assert config["guest_access"] is False
    assert config["guest_limits"] is None
    assert "trial" not in config

    set_instance_setting("guest_access", True)
    config = client.get("/config/public").json()
    assert config["guest_access"] is True
    assert config["guest_limits"] == {
        "max_nodes": 10000,
        "max_output_steps": 50,
        "max_job_minutes": 10,
        "max_concurrent_jobs": 1,
        "retention_days": 1,
    }


def test_admin_settings_include_guest_settings(client):
    admin = _signup(client, "a@x.de")
    settings = client.get("/admin/settings", headers=_auth(admin)).json()
    assert settings["guest_access"] is False
    assert settings["guest_max_output_steps"] == 50

    settings.update(guest_access=True, guest_max_job_minutes=5)
    r = client.put("/admin/settings", json=settings, headers=_auth(admin))
    assert r.status_code == 200, r.text
    assert r.json()["guest_max_job_minutes"] == 5
    assert {"guest_access", "guest_max_job_minutes"} <= set(r.json()["overridden"])


def test_guest_endpoint_disabled_by_default(client):
    assert client.post("/auth/guest").status_code == 404
    assert client.post("/auth/trial-id").status_code in (404, 405)


def test_guest_account_bypasses_closed_signup(client):
    set_instance_setting("guest_access", True)
    set_instance_setting("signup_open", False)
    guest = client.post("/auth/guest").json()
    assert guest["role"] == "guest"
    assert guest["display_name"].startswith("Guest-")
    me = client.get("/auth/me", headers=_auth(guest)).json()
    assert me["role"] == "guest" and me["auth_provider"] == "guest"


def test_guest_is_never_first_admin_and_not_listed(client):
    set_instance_setting("guest_access", True)
    guest = client.post("/auth/guest").json()
    admin = _signup(client, "a@x.de")  # first real account, even with a guest already in the DB
    assert admin["role"] == "admin"
    assert guest["role"] == "guest"
    users = client.get("/admin/users", headers=_auth(admin)).json()
    assert [u["email"] for u in users] == ["a@x.de"]
    r = client.patch(f"/admin/users/{admin['user_id']}", json={"role": "guest"}, headers=_auth(admin))
    assert r.status_code == 422


def test_first_signup_allowed_when_closed_even_with_guests(client):
    set_instance_setting("guest_access", True)
    set_instance_setting("signup_open", False)
    client.post("/auth/guest")
    assert _signup(client, "a@x.de")["role"] == "admin"


def _guest(client):
    set_instance_setting("guest_access", True)
    return client.post("/auth/guest").json()


def _dogbone():
    with open("./models/Dogbone/Dogbone.json", encoding="UTF-8") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/workspaces/Dogbone/Default/files", {}),
        ("put", "/workspaces/Dogbone/Default/input-deck?input_string=x", {}),
        ("post", "/results/analysis?model_name=Dogbone&analysis_id=x", {"json": {}}),
        ("get", "/library/material", {}),
        ("get", "/projects", {}),
        ("get", "/teams", {}),
    ],
)
def test_guest_is_blocked(client, method, url, kwargs):
    guest = _guest(client)
    r = getattr(client, method)(url, headers=_auth(guest), **kwargs)
    assert r.status_code == 403, r.text
    assert "log in for full access" in r.json()["detail"]


def test_apply_guest_limits_clamps_outputs():
    data = ModelData(**_dogbone())
    data.outputs[0].numberOfOutputSteps = 500
    data.outputs[0].useOutputFrequency = True
    apply_guest_limits(data, {"max_output_steps": 50})
    assert all(o.numberOfOutputSteps <= 50 and o.useOutputFrequency is False for o in data.outputs)


def _generate(client, headers, params):
    valves = client.get("/models/Dogbone/params").json()
    return client.post("/workspaces/Dogbone/Default/generate", json={"data": params, "valves": valves}, headers=headers)


@pytest.fixture
def isolated(monkeypatch, tmp_path):
    """Keep generate/run tests away from the real simulations folder and PeriLab API."""
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: _FakeBackend())
    monkeypatch.setattr(jobs, "get_solver_backend", lambda: _FakeBackend())


def _guest_headers(guest):
    return _auth(guest)


def test_guest_node_cap_and_deviations(client, isolated):
    guest = _guest(client)
    set_instance_setting("guest_max_nodes", 1)
    r = _generate(client, _guest_headers(guest), _dogbone())
    assert r.status_code == 404 and "allowed 1" in r.json()["detail"]

    params = _dogbone()
    params["deviations"] = {"enabled": True, "sampleSize": 2, "parameters": []}
    r = _generate(client, _guest_headers(guest), params)
    assert r.status_code == 403


def test_generate_requires_login_with_db(client, isolated):
    r = _generate(client, {"userName": "Guest-deadbeef"}, _dogbone())
    assert r.status_code == 401, r.text


def test_guest_run_rejects_batches(client, isolated):
    guest = _guest(client)
    r = client.post(
        "/jobs?model_name=Dogbone&model_folder_name=Default&job_ids=1,2",
        json=_dogbone(),
        headers=_guest_headers(guest),
    )
    assert r.status_code == 403, r.text


def test_signup_rejects_reserved_guest_names(client):
    r = client.post("/auth/signup", json={"email": "a@x.de", "password": "password123", "display_name": "guest-1234"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Display names starting with 'Guest-' are reserved."


class _FakeClient:
    """Reports every job as still in `status` (default "running", an active
    status per PeriLabJob._ACTIVE_JOB_STATUSES) so sync_status leaves the
    entry alone unless a test asks it to report a finished status."""

    def __init__(self, status="running"):
        self.status = status
        self.deleted = []
        self.log = ""
        self.log_requests = []

    def get_job(self, job_id):
        return PeriLabJob(job_id=job_id, status=self.status)

    def delete_job(self, job_id):
        self.deleted.append(job_id)

    def list_files(self, job_id):
        return []

    def get_log(self, job_id, tail=None):
        self.log_requests.append((job_id, tail))
        return self.log


class _FakeBackend:
    def __init__(self, status="running"):
        self.cancelled = []
        self._client = _FakeClient(status)

    def cancel(self, perilab_job_id):
        self.cancelled.append(perilab_job_id)

    def client(self):
        return self._client


def _job(db, user_id, minutes_ago, job_id):
    entry = JobQueueEntry(
        user_id=user_id,
        model_name="Dogbone",
        model_folder_name="Default",
        remotepath="/x",
        status=JOB_RUNNING,
        perilab_job_id=job_id,
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
        started_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
    )
    db.add(entry)
    db.commit()
    return entry.id


def test_sweep_stops_overdue_guest_jobs_only(client, monkeypatch):
    backend = _FakeBackend()
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: backend)
    guest = _guest(client)
    member = _signup(client, "a@x.de")
    with base.SessionLocal() as db:
        overdue = _job(db, guest["user_id"], 30, "g-old")
        fresh = _job(db, guest["user_id"], 1, "g-new")
        members = _job(db, member["user_id"], 30, "m-old")
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=False)
        status = {e.id: (e.status, e.error) for e in db.query(JobQueueEntry)}
    assert status[overdue] == (JOB_CANCELLED, "Stopped: guest time limit (10 min)")
    assert status[fresh][0] == JOB_RUNNING
    assert status[members][0] == JOB_RUNNING
    assert backend.cancelled == ["g-old"]


def test_sweep_syncs_before_stopping_overdue_job(client, monkeypatch):
    """A guest job PeriLab already finished (but nobody polled, so it's still
    RUNNING in the DB) must be synced to its real status instead of getting
    cancelled and mislabelled "Stopped: guest time limit"."""
    backend = _FakeBackend(status="completed")
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: backend)
    guest = _guest(client)
    with base.SessionLocal() as db:
        overdue = _job(db, guest["user_id"], 30, "g-finished")
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=False)
        entry = db.get(JobQueueEntry, overdue)
        result = (entry.status, entry.error)
    assert result == (JOB_DONE, None)
    assert backend.cancelled == []


def test_sweep_deletes_expired_guests_with_data(client, monkeypatch, tmp_path):
    backend = _FakeBackend()
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: backend)
    monkeypatch.setattr(guest_sweeper, "get_solver_backend", lambda: backend)
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    old_guest = _guest(client)
    new_guest = client.post("/auth/guest").json()
    os.makedirs(tmp_path / old_guest["user_id"] / "Dogbone")
    with base.SessionLocal() as db:
        _job(db, old_guest["user_id"], 1, "g-1")
        db.get(User, old_guest["user_id"]).created_at = datetime.now(timezone.utc) - timedelta(days=2)
        db.commit()
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=True)
        remaining = {u.id for u in db.query(User)}
        jobs = db.query(JobQueueEntry).count()
    assert remaining == {new_guest["user_id"]}
    assert jobs == 0
    assert backend.client().deleted == ["g-1"]
    assert not (tmp_path / old_guest["user_id"]).exists()
    # the expired guest's session no longer resolves
    assert client.get("/auth/me", headers=_auth(old_guest)).status_code == 401
