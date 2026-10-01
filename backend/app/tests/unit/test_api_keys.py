# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from backend.app.support.api_keys import KEY_PREFIX_LEN


def _signup(client, email="a@x.de"):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_api_key_lifecycle(client):
    auth = _signup(client)
    r = client.post("/auth/api-keys", json={"name": "ci"}, headers=auth)
    assert r.status_code == 200, r.text
    created = r.json()
    assert created["key"].startswith("phk_")
    assert created["prefix"] == created["key"][:KEY_PREFIX_LEN]

    listed = client.get("/auth/api-keys", headers=auth).json()
    assert [k["name"] for k in listed] == ["ci"]
    assert "key" not in listed[0]

    me = client.get("/auth/me", headers={"X-Api-Key": created["key"]})
    assert me.status_code == 200 and me.json()["email"] == "a@x.de"

    assert client.delete(f"/auth/api-keys/{created['id']}", headers=auth).status_code == 204
    assert client.get("/auth/me", headers={"X-Api-Key": created["key"]}).status_code == 401
    assert client.get("/auth/api-keys", headers=auth).json() == []


def test_cannot_revoke_someone_elses_key(client):
    owner = _signup(client, "a@x.de")
    other = _signup(client, "b@x.de")
    key_id = client.post("/auth/api-keys", json={"name": "ci"}, headers=owner).json()["id"]
    assert client.delete(f"/auth/api-keys/{key_id}", headers=other).status_code == 404


def test_guests_and_anonymous_cannot_create_keys(client):
    from .conftest import set_instance_setting

    assert client.post("/auth/api-keys", json={"name": "x"}).status_code == 401
    set_instance_setting("guest_access", True)
    guest = client.post("/auth/guest").json()
    r = client.post("/auth/api-keys", json={"name": "x"}, headers={"Authorization": f"Bearer {guest['token']}"})
    assert r.status_code == 403


def test_key_name_is_required(client):
    auth = _signup(client)
    assert client.post("/auth/api-keys", json={"name": "  "}, headers=auth).status_code == 422
