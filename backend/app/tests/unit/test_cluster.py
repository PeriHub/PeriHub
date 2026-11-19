import json

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from backend.app.db import base
from backend.app.db.models import JOB_RUNNING, JobQueueEntry, User
from backend.app.ee import cluster
from backend.app.support import entitlements
from backend.app.support.solver_backend import get_solver_backend

from .conftest import set_instance_setting

PROFILE = {
    "host": "CARA.dlr.de",
    "username": "f_peridi",
    "account": "2263032",
    "perilab_path": "$HOME/perilab",
}


def _signup(client, email="a@x.de"):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    with base.SessionLocal() as db:
        user_id = db.scalar(select(User.id).where(User.email == email))
    return {"Authorization": f"Bearer {r.json()['token']}"}, user_id


@pytest.fixture(autouse=True)
def unlicensed(monkeypatch):
    """No license server = nothing gated, whatever LICENSE_SERVER_URL the developer's .env sets."""
    monkeypatch.setattr(entitlements, "license_server_url", "")


@pytest.fixture
def secret(monkeypatch):
    monkeypatch.setattr(cluster, "session_secret", "test-secret")


def test_profile_host_must_be_allowed(client, secret):
    auth, _ = _signup(client)
    assert client.put("/cluster/profile", json=PROFILE, headers=auth).status_code == 400  # list empty = off
    set_instance_setting("cluster_allowed_hosts", "cara.dlr.de")
    assert client.put("/cluster/profile", json={**PROFILE, "host": "perihub_db"}, headers=auth).status_code == 400
    r = client.put("/cluster/profile", json=PROFILE, headers=auth)
    assert r.status_code == 200, r.text
    assert r.json()["workdir"] == "~/perihub" and r.json()["job_template"] is None


def test_generated_key_is_public_only(client, secret):
    set_instance_setting("cluster_allowed_hosts", "cara.dlr.de")
    auth, _ = _signup(client)
    client.put("/cluster/profile", json=PROFILE, headers=auth)
    r = client.post("/cluster/profile/key", headers=auth)
    assert r.status_code == 200, r.text
    assert r.json()["public_key"].startswith("ssh-ed25519 ")
    profile = client.get("/cluster/profile", headers=auth).json()
    assert profile["public_key"] == r.json()["public_key"]
    assert "private_key_enc" not in profile and "PRIVATE" not in str(profile)


def test_bad_paths_are_rejected(client, secret):
    set_instance_setting("cluster_allowed_hosts", "cara.dlr.de")
    auth, _ = _signup(client)
    r = client.put("/cluster/profile", json={**PROFILE, "perilab_path": "x'; rm -rf ~"}, headers=auth)
    assert r.status_code == 422


def test_host_removed_from_list_stops_the_solver(client, secret):
    set_instance_setting("cluster_allowed_hosts", "cara.dlr.de")
    auth, user_id = _signup(client)
    client.put("/cluster/profile", json=PROFILE, headers=auth)
    client.post("/cluster/profile/key", headers=auth)
    set_instance_setting("cluster_allowed_hosts", "")
    with pytest.raises(HTTPException) as exc:
        get_solver_backend("cluster", user_id)
    assert exc.value.status_code == 400


def test_profile_locked_while_a_cluster_run_is_active(client, secret):
    set_instance_setting("cluster_allowed_hosts", "cara.dlr.de")
    auth, user_id = _signup(client)
    client.put("/cluster/profile", json=PROFILE, headers=auth)
    with base.SessionLocal() as db:
        db.add(
            JobQueueEntry(
                user_id=user_id,
                model_name="m",
                model_folder_name="f",
                remotepath="/x",
                status=JOB_RUNNING,
                solver="cluster",
            )
        )
        db.commit()
    assert client.put("/cluster/profile", json={**PROFILE, "username": "other"}, headers=auth).status_code == 409
    assert client.put("/cluster/profile", json={**PROFILE, "time_limit": "02:00:00"}, headers=auth).status_code == 200
    assert client.post("/cluster/profile/key", headers=auth).status_code == 409
    assert client.delete("/cluster/profile", headers=auth).status_code == 409


def test_guests_cannot_use_cluster(client):
    set_instance_setting("guest_access", True)
    guest = {"Authorization": f"Bearer {client.post('/auth/guest').json()['token']}"}
    assert client.get("/cluster/profile", headers=guest).status_code == 403
    with open("models/Dogbone/Dogbone.json") as file:
        model_data = json.load(file)
    r = client.post("/jobs?model_name=Dogbone&solver=cluster", json=model_data, headers=guest)
    assert r.status_code == 403, r.text
