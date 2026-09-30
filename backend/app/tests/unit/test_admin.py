# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import models  # noqa: F401 - registers tables on Base.metadata
from backend.app.db import base
from backend.app.main import app


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(base, "SessionLocal", session_local)

    def get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[base.get_db] = get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _signup(client, email):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    return r.json()


def _auth(body):
    return {"Authorization": f"Bearer {body['token']}"}


def test_first_user_is_admin_second_is_member(client):
    assert _signup(client, "a@x.de")["role"] == "admin"
    assert _signup(client, "b@x.de")["role"] == "member"


def test_non_admin_gets_403(client):
    _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    assert client.get("/admin/users", headers=_auth(member)).status_code == 403
    assert client.get("/admin/users").status_code == 401


def test_admin_lists_and_updates_users(client):
    admin = _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    users = client.get("/admin/users", headers=_auth(admin)).json()
    assert {u["email"] for u in users} == {"a@x.de", "b@x.de"}

    r = client.patch(f"/admin/users/{member['user_id']}", json={"role": "viewer"}, headers=_auth(admin))
    assert r.status_code == 200 and r.json()["role"] == "viewer"
    r = client.patch(f"/admin/users/{member['user_id']}", json={"role": "boss"}, headers=_auth(admin))
    assert r.status_code == 422


def test_last_admin_cannot_be_removed(client):
    admin = _signup(client, "a@x.de")
    for change in ({"role": "member"}, {"is_active": False}):
        r = client.patch(f"/admin/users/{admin['user_id']}", json=change, headers=_auth(admin))
        assert r.status_code == 409, change


def test_deactivated_user_cannot_log_in(client):
    admin = _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    client.patch(f"/admin/users/{member['user_id']}", json={"is_active": False}, headers=_auth(admin))
    r = client.post("/auth/login", json={"email": "b@x.de", "password": "password123"})
    assert r.status_code == 403


def test_settings_round_trip_and_closed_signup(client):
    admin = _signup(client, "a@x.de")
    settings = client.get("/admin/settings", headers=_auth(admin)).json()
    assert settings["overridden"] == []

    settings.update(signup_open=False, default_role="viewer")
    r = client.put("/admin/settings", json=settings, headers=_auth(admin))
    assert r.status_code == 200, r.text
    assert set(r.json()["overridden"]) >= {"signup_open", "default_role"}

    r = client.post("/auth/signup", json={"email": "c@x.de", "password": "password123", "display_name": "c"})
    assert r.status_code == 403

    settings.update(signup_open=True)
    client.put("/admin/settings", json=settings, headers=_auth(admin))
    assert _signup(client, "c@x.de")["role"] == "viewer"


def test_usage_all_is_gone_and_admin_usage_works(client):
    admin = _signup(client, "a@x.de")
    assert client.get("/usage/all").status_code in (404, 405)
    assert client.get("/admin/usage", headers=_auth(admin)).status_code == 200
    assert client.get("/admin/jobs", headers=_auth(admin)).json() == []
    assert client.get("/admin/audit-log", headers=_auth(admin)).status_code == 200


def test_only_developers_and_admins_create_models(client, monkeypatch, tmp_path):
    from backend.app.routers import model as model_router

    monkeypatch.setattr(model_router, "OWN_MODELS", tmp_path)
    admin = _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    params = {"model_name": "My Model", "description": "d"}

    assert client.post("/models", params=params).status_code == 401
    assert client.post("/models", params=params, headers=_auth(member)).status_code == 403
    assert client.put("/models/my_model/source", json={"source_code": "x"}, headers=_auth(member)).status_code == 403
    assert client.delete("/models/my_model", headers=_auth(member)).status_code == 403
    assert client.put("/models/Dogbone/config", json={}, headers=_auth(member)).status_code == 403

    client.patch(f"/admin/users/{member['user_id']}", json={"role": "developer"}, headers=_auth(admin))
    assert client.post("/models", params=params, headers=_auth(member)).status_code == 200
    assert client.delete("/models/my_model", headers=_auth(admin)).status_code == 200
