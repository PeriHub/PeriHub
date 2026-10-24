# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import re
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from backend.app.db import base
from backend.app.db.models import JOB_DONE, JobQueueEntry, ModelConfig, Project, ProjectMembership, User
from backend.app.routers import auth, oauth
from backend.app.support import account, external_identity, guest_sweeper, job_notifications, job_queue
from backend.app.support.file_handler import FileHandler

from .conftest import set_instance_setting
from .test_guest import _FakeBackend, _job


def _signup(client, email, password="password123"):
    r = client.post("/auth/signup", json={"email": email, "password": password, "display_name": email})
    assert r.status_code == 200, r.text
    return r.json()


def _auth(body):
    return {"Authorization": f"Bearer {body['token']}"}


def _login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password}).status_code


@pytest.fixture
def mailbox(monkeypatch):
    sent = []
    monkeypatch.setattr(auth, "mail_enabled", lambda: True)
    monkeypatch.setattr(auth, "public_url", "https://perihub.example.com")
    monkeypatch.setattr(auth, "send_mail", lambda to, subject, body: sent.append((to, body)) or True)
    monkeypatch.setattr(auth, "_last_reset_mail", {})
    return sent


def _reset_token(body):
    return re.search(r"/auth/reset\?token=(\S+)", body).group(1)


def test_change_password(client):
    user = _signup(client, "a@x.de")
    r = client.post(
        "/auth/password", json={"current_password": "wrong", "new_password": "newpass123"}, headers=_auth(user)
    )
    assert r.status_code == 401
    r = client.post(
        "/auth/password", json={"current_password": "password123", "new_password": "short"}, headers=_auth(user)
    )
    assert r.status_code == 422
    r = client.post(
        "/auth/password", json={"current_password": "password123", "new_password": "newpass123"}, headers=_auth(user)
    )
    assert r.status_code == 204
    assert _login(client, "a@x.de", "password123") == 401
    assert _login(client, "a@x.de", "newpass123") == 200


def test_login_throttled_after_repeated_failures(client):
    _signup(client, "a@x.de")
    for _ in range(auth._LOGIN_MAX_FAILURES):
        assert _login(client, "a@x.de", "wrongpass") == 401
    # Blocked even with the right password (and regardless of case), so guessing can't continue.
    assert _login(client, "A@x.de", "password123") == 429
    auth._login_failures.clear()  # window expired
    assert _login(client, "a@x.de", "password123") == 200


def test_forgot_password_unavailable_without_mail(client):
    assert client.get("/config/public").json()["password_reset"] is False
    assert client.post("/auth/password/forgot", json={"email": "a@x.de"}).status_code == 404


def test_forgot_and_reset_password(client, mailbox):
    user = _signup(client, "a@x.de")
    # same answer for unknown addresses, and no mail
    assert client.post("/auth/password/forgot", json={"email": "nobody@x.de"}).status_code == 202
    assert client.post("/auth/password/forgot", json={"email": "a@x.de"}).status_code == 202
    assert client.post("/auth/password/forgot", json={"email": "a@x.de"}).status_code == 202  # cooldown: no 2nd mail
    assert [to for to, _ in mailbox] == ["a@x.de"]
    token = _reset_token(mailbox[0][1])
    assert mailbox[0][1].count("https://perihub.example.com/auth/reset?token=") == 1

    # a reset token is not a session
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401

    assert client.post("/auth/password/reset", json={"token": token, "new_password": "x"}).status_code == 422
    assert client.post("/auth/password/reset", json={"token": token, "new_password": "newpass123"}).status_code == 204
    assert _login(client, "a@x.de", "newpass123") == 200
    # single use: the password changed, so the link is dead
    r = client.post("/auth/password/reset", json={"token": token, "new_password": "again1234"})
    assert r.status_code == 400
    assert client.post("/auth/password/reset", json={"token": "garbage", "new_password": "x" * 8}).status_code == 400
    assert user  # the old session is still valid
    assert client.get("/auth/me", headers=_auth(user)).status_code == 200


def test_delete_account_removes_everything_it_owns(client, monkeypatch, tmp_path):
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    admin = _signup(client, "admin@x.de")
    user = _signup(client, "u@x.de")
    (tmp_path / user["user_id"] / "Dogbone").mkdir(parents=True)
    with base.SessionLocal() as db:
        org_id = db.get(User, user["user_id"]).org_id
        project = Project(org_id=org_id, name="p", created_by=user["user_id"])
        db.add(project)
        db.flush()
        db.add(ProjectMembership(project_id=project.id, user_id=admin["user_id"]))
        db.add(ModelConfig(owner_id=user["user_id"], org_id=org_id, name="mine", config={}, visibility="public"))
        others = ModelConfig(owner_id=admin["user_id"], org_id=org_id, project_id=project.id, name="theirs", config={})
        db.add(others)
        db.commit()
        others_id = others.id

    r = client.post("/auth/me/delete", json={"password": "wrong"}, headers=_auth(user))
    assert r.status_code == 401
    r = client.post("/auth/me/delete", json={"password": "password123"}, headers=_auth(user))
    assert r.status_code == 204

    assert client.get("/auth/me", headers=_auth(user)).status_code == 401
    assert not (tmp_path / user["user_id"]).exists()
    with base.SessionLocal() as db:
        assert db.get(User, user["user_id"]) is None
        assert db.query(Project).count() == 0
        assert db.query(ProjectMembership).count() == 0
        assert [c.name for c in db.query(ModelConfig)] == ["theirs"]
        assert db.get(ModelConfig, others_id).project_id is None


def test_last_admin_and_guests_cannot_delete(client):
    admin = _signup(client, "admin@x.de")
    r = client.post("/auth/me/delete", json={"password": "password123"}, headers=_auth(admin))
    assert r.status_code == 409
    set_instance_setting("guest_access", True)
    guest = client.post("/auth/guest").json()
    assert client.post("/auth/me/delete", json={}, headers=_auth(guest)).status_code == 403
    assert client.post("/auth/me/delete", json={"password": "x"}).status_code == 401


def test_oauth_account_confirms_with_email(client, monkeypatch):
    monkeypatch.setattr(account, "get_solver_backend", lambda: None)  # no jobs, never called
    _signup(client, "admin@x.de")
    user = _signup(client, "sso@x.de")
    with base.SessionLocal() as db:
        row = db.get(User, user["user_id"])
        row.auth_provider, row.password_hash = "oauth", None
        db.commit()
    assert client.post("/auth/me/delete", json={"email": "other@x.de"}, headers=_auth(user)).status_code == 401
    assert client.post("/auth/me/delete", json={"email": "SSO@x.de"}, headers=_auth(user)).status_code == 204


@pytest.fixture
def outbox(monkeypatch):
    """Job notification mails, sent inline instead of on a thread."""
    sent = []

    class InlineThread:
        def __init__(self, target, args, daemon):
            self.run = lambda: target(*args)

        def start(self):
            self.run()

    monkeypatch.setattr(job_notifications, "smtp_configured", lambda: True)
    monkeypatch.setattr(job_notifications, "send_mail", lambda to, subject, body: sent.append((to, subject, body)))
    monkeypatch.setattr(job_notifications, "Thread", InlineThread)
    return sent


def _notify_on(client, user, on=True):
    r = client.patch("/auth/me", json={"notify_job_emails": on}, headers=_auth(user))
    assert r.status_code == 200, r.text
    assert r.json()["notify_job_emails"] is on


def test_job_notification_setting(client):
    user = _signup(client, "a@x.de")
    assert client.get("/auth/me", headers=_auth(user)).json()["notify_job_emails"] is False
    _notify_on(client, user)
    assert client.get("/auth/me", headers=_auth(user)).json()["notify_job_emails"] is True
    set_instance_setting("guest_access", True)
    guest = client.post("/auth/guest").json()
    assert client.patch("/auth/me", json={"notify_job_emails": True}, headers=_auth(guest)).status_code == 403
    assert client.get("/config/public").json()["job_notifications"] is False


def test_background_sync_mails_finished_run_once(client, monkeypatch, outbox):
    backend = _FakeBackend(status="completed")
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: backend)
    opted_in = _signup(client, "a@x.de")
    other = _signup(client, "b@x.de")
    _notify_on(client, opted_in)
    with base.SessionLocal() as db:
        mine = _job(db, opted_in["user_id"], 5, "p-1")
        _job(db, other["user_id"], 5, "p-2")
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=False)
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=False)
        assert db.get(JobQueueEntry, mine).status == JOB_DONE
    assert [(to, subject) for to, subject, _ in outbox] == [("a@x.de", "PeriHub: Dogbone / Default finished")]
    assert "Run time: 5m" in outbox[0][2]


def test_own_cancel_sends_nothing_but_perilab_stop_does(client, monkeypatch, outbox):
    backend = _FakeBackend()
    monkeypatch.setattr(job_queue, "get_solver_backend", lambda: backend)
    user = _signup(client, "u@x.de")
    _notify_on(client, user)
    with base.SessionLocal() as db:
        own = _job(db, user["user_id"], 1, "p-own")
        elsewhere = _job(db, user["user_id"], 1, "p-elsewhere")
    assert client.put(f"/jobs/{own}/cancel", headers=_auth(user)).status_code == 200
    backend.client().status = "cancelled"  # stopped on the PeriLab side
    with base.SessionLocal() as db:
        guest_sweeper.sweep(db, datetime.now(timezone.utc), retention=False)
        assert db.get(JobQueueEntry, elsewhere).status == "cancelled"
    assert [subject for _, subject, _ in outbox] == ["PeriHub: Dogbone / Default was stopped"]


@pytest.fixture
def idp(monkeypatch):
    """OIDC callback without an IdP or license server: set `idp.userinfo` before calling /oauth/oidc/callback."""
    state = SimpleNamespace(userinfo={})
    monkeypatch.setattr(oauth, "require_feature", lambda feature: None)
    monkeypatch.setattr(oauth, "get_status", lambda: SimpleNamespace(plan="enterprise"))
    monkeypatch.setattr(oauth, "exchange_code_for_userinfo", lambda code: state.userinfo)
    return state


def _oidc_login(client, idp, **userinfo):
    idp.userinfo = userinfo
    r = client.get("/oauth/oidc/callback", params={"code": "c"})
    assert r.status_code == 200, r.text
    return r.json()


def test_oauth_claims_are_configurable_and_synced(client, idp, monkeypatch):
    monkeypatch.setattr(oauth, "oauth_email_claims", ["email", "upn"])
    monkeypatch.setattr(oauth, "oauth_name_claims", ["name"])
    first = _oidc_login(client, idp, sub="s1", upn="jo@corp.de", name="Jo", preferred_username="jdoe1")
    me = client.get("/auth/me", headers=_auth(first)).json()
    assert (me["email"], me["display_name"]) == ("jo@corp.de", "Jo")
    # changed at the IdP: picked up on the next login, same account
    again = _oidc_login(client, idp, sub="s1", email="jo.new@corp.de", name="Jo Doe")
    me = client.get("/auth/me", headers=_auth(again)).json()
    assert (again["user_id"], me["email"], me["display_name"]) == (first["user_id"], "jo.new@corp.de", "Jo Doe")


def test_oauth_never_takes_another_accounts_email(client, idp):
    _signup(client, "taken@x.de")
    new = _oidc_login(client, idp, sub="s2", email="taken@x.de", preferred_username="jo")
    assert client.get("/auth/me", headers=_auth(new)).json()["email"] is None
    _oidc_login(client, idp, sub="s2", email="taken@x.de", preferred_username="jo")  # no crash on sync either


def test_oauth_account_without_email_confirms_delete_with_text(client, idp):
    _signup(client, "admin@x.de")
    user = _oidc_login(client, idp, sub="s3", preferred_username="noemail")
    assert client.post("/auth/me/delete", json={"confirm": "delete"}, headers=_auth(user)).status_code == 401
    assert client.post("/auth/me/delete", json={"confirm": "DELETE"}, headers=_auth(user)).status_code == 204


def test_closed_signup_only_stops_email_registration(client, idp):
    _signup(client, "admin@x.de")
    set_instance_setting("signup_open", False)
    r = client.post("/auth/signup", json={"email": "b@x.de", "password": "password123", "display_name": "b"})
    assert r.status_code == 403
    _oidc_login(client, idp, sub="s4", email="sso@x.de", preferred_username="sso")  # 200: SSO still gets in


def test_oauth_picture_claim(client, idp):
    first = _oidc_login(client, idp, sub="s5", email="p@x.de", picture="https://idp.example/p.png")
    assert client.get("/auth/me", headers=_auth(first)).json()["avatar_url"] == "https://idp.example/p.png"
    again = _oidc_login(client, idp, sub="s5", email="p@x.de", picture="javascript:alert(1)")
    assert client.get("/auth/me", headers=_auth(again)).json()["avatar_url"] is None
    assert client.get("/auth/me", headers=_auth(_signup(client, "local@x.de"))).json()["avatar_url"] is None


def test_sso_links_to_existing_account_by_verified_email(client, idp, monkeypatch):
    local = _signup(client, "Jo@x.de")
    # unverified: separate account, the email stays with the local one
    other = _oidc_login(client, idp, sub="s6", email="jo@x.de", email_verified=False, preferred_username="jo")
    assert other["user_id"] != local["user_id"]
    # verified (case-insensitive): signs into the existing account, password still works
    linked = _oidc_login(client, idp, sub="s7", email="jo@x.de", email_verified=True, preferred_username="jo")
    assert linked["user_id"] == local["user_id"]
    assert _oidc_login(client, idp, sub="s7", email="jo@x.de", email_verified=True)["user_id"] == local["user_id"]
    assert _login(client, "Jo@x.de", "password123") == 200
    # switched off: never links
    monkeypatch.setattr(external_identity, "oauth_link_by_email", False)
    off = _oidc_login(client, idp, sub="s8", email="jo@x.de", email_verified=True, preferred_username="jo")
    assert off["user_id"] != local["user_id"]


def test_verified_flag_only_covers_the_email_claim(client, idp, monkeypatch):
    local = _signup(client, "jo@corp.de")
    monkeypatch.setattr(oauth, "oauth_email_claims", ["upn"])
    r = _oidc_login(client, idp, sub="s9", upn="jo@corp.de", email="else@corp.de", email_verified=True)
    assert r["user_id"] != local["user_id"]


def test_trusted_idp_links_without_email_verified(client, idp, monkeypatch):
    local = _signup(client, "jo@corp.de")
    assert _oidc_login(client, idp, sub="t1", email="jo@corp.de")["user_id"] != local["user_id"]
    monkeypatch.setattr(oauth, "oauth_trust_email", True)
    assert _oidc_login(client, idp, sub="t2", email="jo@corp.de")["user_id"] == local["user_id"]
