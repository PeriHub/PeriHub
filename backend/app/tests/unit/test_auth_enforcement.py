# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from starlette.requests import Request

from backend.app.db import base
from backend.app.db.models import ApiKey, User
from backend.app.support.api_keys import generate_key, hash_key
from backend.app.support.db_auth import resolve_user


def _request(headers: dict) -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": raw})


def _signup(client, email="a@x.de"):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    return r.json()


def test_username_header_alone_resolves_nobody(client):
    _signup(client)
    with base.SessionLocal() as db:
        identity = resolve_user(_request({"userName": "a@x.de"}), db)
    assert identity.user is None
    assert identity.username == ""


def test_bearer_resolves_user_id(client):
    body = _signup(client)
    with base.SessionLocal() as db:
        identity = resolve_user(_request({"Authorization": f"Bearer {body['token']}"}), db)
    assert identity.user.id == body["user_id"]
    assert identity.username == body["user_id"]


def test_api_key_resolves_owner_and_tracks_last_use(client):
    body = _signup(client)
    key = generate_key()
    with base.SessionLocal() as db:
        db.add(ApiKey(user_id=body["user_id"], name="ci", prefix=key[:12], key_hash=hash_key(key)))
        db.commit()
        identity = resolve_user(_request({"X-Api-Key": key}), db)
        assert identity.user.id == body["user_id"]
        assert db.query(ApiKey).one().last_used_at is not None


def test_unknown_or_revoked_api_key_resolves_nobody(client):
    from datetime import datetime, timezone

    body = _signup(client)
    key = generate_key()
    with base.SessionLocal() as db:
        db.add(
            ApiKey(
                user_id=body["user_id"],
                name="old",
                prefix=key[:12],
                key_hash=hash_key(key),
                revoked_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        assert resolve_user(_request({"X-Api-Key": key}), db).user is None
        assert resolve_user(_request({"X-Api-Key": generate_key()}), db).user is None


def test_generate_key_format():
    key = generate_key()
    assert key.startswith("phk_") and len(key) > 40
    assert generate_key() != key
    assert len(hash_key(key)) == 64
