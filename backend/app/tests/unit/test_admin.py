# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0


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


def _foreign_user():
    """A user in a second organization (signup always lands in the default one)."""
    from backend.app.db import base
    from backend.app.db.models import Organization, User
    from backend.app.support.local_auth import create_session_token

    with base.SessionLocal() as db:
        org = Organization(name="Other", plan="enterprise")
        db.add(org)
        db.flush()
        user = User(email="f@y.de", display_name="f", auth_provider="local", role="admin", org_id=org.id)
        db.add(user)
        db.commit()
        return {"user_id": user.id, "token": create_session_token(user.id)}


def test_teams_stay_within_the_org(client):
    admin = _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    foreign = _foreign_user()
    team = client.post("/teams", json={"name": "T"}, headers=_auth(admin)).json()

    assert client.post(f"/teams/{team['id']}/members/{foreign['user_id']}", headers=_auth(admin)).status_code == 404
    assert client.post(f"/teams/{team['id']}/members/{member['user_id']}", headers=_auth(admin)).status_code == 200
    # Another org's admin can neither see the team nor remove its members.
    r = client.delete(f"/teams/{team['id']}/members/{member['user_id']}", headers=_auth(foreign))
    assert r.status_code == 404


def test_project_members_stay_within_the_org(client):
    owner = _signup(client, "a@x.de")
    foreign = _foreign_user()
    project = client.post("/projects", json={"name": "P"}, headers=_auth(owner)).json()

    r = client.post(f"/projects/{project['id']}/members", json={"user_id": foreign["user_id"]}, headers=_auth(owner))
    assert r.status_code == 404


def test_library_items_only_shared_into_own_teams(client):
    admin = _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    team = client.post("/teams", json={"name": "T"}, headers=_auth(admin)).json()
    item = {"name": "cfg", "visibility": "team", "team_id": team["id"], "config": {}}

    assert client.post("/library/model-config", json=item, headers=_auth(member)).status_code == 403
    client.post(f"/teams/{team['id']}/members/{member['user_id']}", headers=_auth(admin))
    assert client.post("/library/model-config", json=item, headers=_auth(member)).status_code == 200
    assert client.post("/library/model-config", json=item, headers=_auth(_foreign_user())).status_code == 404


def test_model_source_and_license_refresh_need_rights(client):
    _signup(client, "a@x.de")
    member = _signup(client, "b@x.de")
    assert client.get("/models/Anything/source").status_code == 401
    assert client.post("/license/refresh").status_code == 401
    assert client.post("/license/refresh", headers=_auth(member)).status_code == 403


def test_public_config_reports_whether_signup_is_open(client):
    assert client.get("/config/public").json()["signup_open"] is True  # fresh install: first account always allowed
    admin = _signup(client, "a@x.de")
    settings = client.get("/admin/settings", headers=_auth(admin)).json()
    settings.update(signup_open=False)
    client.put("/admin/settings", json=settings, headers=_auth(admin))
    assert client.get("/config/public").json()["signup_open"] is False
