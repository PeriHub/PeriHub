# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Path-traversal regression tests: Starlette percent-decodes path params (%2E%2E -> ..), so a client-controlled
model_name/model_folder_name/filename segment must never be trusted to stay inside the caller's own folder."""

import os

import pytest

from backend.app.support.file_handler import FileHandler, safe_segment


def _signup(client, email="a@x.de"):
    r = client.post("/auth/signup", json={"email": email, "password": "password123", "display_name": email})
    assert r.status_code == 200, r.text
    body = r.json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user_id"]


@pytest.fixture
def sim_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    return tmp_path


def test_download_rejects_traversal_into_another_users_folder(client, sim_dir):
    auth, my_id = _signup(client)
    os.makedirs(sim_dir / my_id)
    other_id = "other-user-id"
    victim_folder = sim_dir / other_id / "Dogbone" / "Default"
    os.makedirs(victim_folder)
    (victim_folder / "secret.txt").write_text("secret")

    r = client.get(f"/workspaces/%2E%2E/{other_id}/download", headers=auth)

    assert r.status_code == 400, r.text
    assert (sim_dir / other_id).exists()


def test_delete_rejects_traversal_into_another_users_folder(client, sim_dir):
    auth, my_id = _signup(client)
    os.makedirs(sim_dir / my_id)
    other_id = "other-user-id"
    victim_folder = sim_dir / other_id / "Dogbone" / "Default"
    os.makedirs(victim_folder)

    r = client.delete(f"/workspaces/%2E%2E/{other_id}", headers=auth)

    assert r.status_code == 400, r.text
    assert (sim_dir / other_id).exists()


def test_upload_rejects_traversal_in_filename(client, sim_dir):
    auth, _ = _signup(client)

    r = client.post(
        "/workspaces/Dogbone/Default/files",
        headers=auth,
        files={"files": ("../../escaped.txt", b"hello world\n" * 5, "text/plain")},
    )

    assert r.status_code == 400, r.text
    assert not (sim_dir / "escaped.txt").exists()
    assert not (sim_dir.parent / "escaped.txt").exists()


@pytest.mark.parametrize(
    "segment, ok",
    [
        (".", False),
        ("..", False),
        ("", False),
        ("a/b", False),
        ("a\\b", False),
        ("Dogbone", True),
        ("Default_1", True),
    ],
)
def test_safe_segment(segment, ok):
    if ok:
        assert safe_segment(segment) == segment
    else:
        with pytest.raises(Exception):
            safe_segment(segment)
