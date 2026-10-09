# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from backend.app.db import base
from backend.app.db.models import Organization, User
from backend.app.support.admin_settings import set_setting


def _signup(client, email):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _create(client, headers, name="Steel", **extra):
    r = client.post("/library/material", json={"name": name, "properties": {"name": name}, **extra}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


def _names(client, headers):
    r = client.get("/library/material", headers=headers)
    assert r.status_code == 200, r.text
    return {m["name"] for m in r.json()}


def test_private_by_default_visible_to_owner_and_org_admin_only(client):
    admin = _signup(client, "admin@x.de")  # first signup becomes admin
    owner = _signup(client, "owner@x.de")
    member = _signup(client, "member@x.de")

    item = _create(client, owner)
    assert item["visibility"] == "private"
    assert item["can_edit"] is True and item["owner_name"] == "owner@x.de"

    assert _names(client, owner) == {"Steel"}
    assert _names(client, member) == set()
    assert [m["can_edit"] for m in client.get("/library/material", headers=admin).json()] == [True]

    # Admins of another organization don't see it.
    with base.SessionLocal() as db:
        other = Organization(name="Other")
        db.add(other)
        db.flush()
        db.query(User).filter(User.email == "admin@x.de").update({"org_id": other.id})
        db.commit()
    assert _names(client, admin) == set()


def test_shared_material_visible_but_only_owner_or_admin_edits(client):
    admin = _signup(client, "admin@x.de")
    owner = _signup(client, "owner@x.de")
    member = _signup(client, "member@x.de")
    item = _create(client, owner, visibility="org")

    listed = client.get("/library/material", headers=member).json()
    assert [(m["name"], m["can_edit"]) for m in listed] == [("Steel", False)]

    body = {"name": "Hacked", "visibility": "org", "properties": {}}
    assert client.put(f"/library/material/{item['id']}", json=body, headers=member).status_code == 403
    assert client.delete(f"/library/material/{item['id']}", headers=member).status_code == 403

    body["name"] = "Steel 2"
    r = client.put(f"/library/material/{item['id']}", json=body, headers=admin)
    assert r.status_code == 200 and r.json()["name"] == "Steel 2"
    assert client.delete(f"/library/material/{item['id']}", headers=owner).status_code == 200
    assert _names(client, owner) == set()


def test_guests_and_anonymous_are_rejected(client):
    assert client.get("/library/material").status_code == 401
    with base.SessionLocal() as db:
        set_setting(db, "guest_access", True)
    token = client.post("/auth/guest").json()["token"]
    assert client.get("/library/material", headers={"Authorization": f"Bearer {token}"}).status_code == 403
