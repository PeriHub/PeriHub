import os
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.app.ee.slurm_client import (
    DEFAULT_TEMPLATE,
    HostKeyMismatch,
    SlurmClient,
    check_host_key,
    render_template,
    slurm_status,
)


class FakeConn:
    """In-memory stand-in for ee.slurm_client.Connection: remote files in a dict, commands recorded."""

    def __init__(self, replies=None):
        self.files: dict[str, bytes] = {}
        self.commands: list[str] = []
        self.replies = replies or {}

    def home(self):
        return "/home/u"

    def run(self, cmd):
        self.commands.append(cmd)
        for prefix, reply in self.replies.items():
            if cmd.startswith(prefix):
                return reply
        return 0, ""

    def put(self, local, remote):
        with open(local, "rb") as file:
            self.files[remote] = file.read()

    def write(self, remote, data):
        self.files[remote] = data

    def read(self, remote):
        return self.files.get(remote)

    def stat(self, remote):
        data = self.files.get(remote)
        return None if data is None else (1, len(data))

    def walk(self, root):
        return sorted(p[len(root) + 1 :] for p in self.files if p.startswith(root + "/"))

    def get(self, remote, local):
        with open(local, "wb") as file:
            file.write(self.files[remote])


def profile(**kw):
    values = dict(
        account="2263032",
        perilab_path="$HOME/perilab",
        workdir="~/perihub",
        partition="",
        time_limit="00:10:00",
        job_template=None,
    )
    values.update(kw)
    return SimpleNamespace(**values)


def test_render_template_keeps_bash_variables():
    assert render_template("${HOME} {{account}}", {"account": "42"}) == "${HOME} 42"


@pytest.mark.parametrize(
    "squeue,exit_code,sacct,expected",
    [
        ("PENDING", None, None, "queued"),
        ("RUNNING", None, None, "running"),
        (None, "0", None, "completed"),
        (None, "1", None, "failed"),
        (None, None, "CANCELLED by 1", "cancelled"),
        (None, None, "TIMEOUT", "failed"),
        (None, None, None, "failed"),
    ],
)
def test_slurm_status(squeue, exit_code, sacct, expected):
    assert slurm_status(squeue, exit_code, sacct) == expected


def test_submit_job_uploads_and_runs_sbatch(tmp_path):
    deck = tmp_path / "Dogbone.yaml"
    deck.write_text("PeriLab: {}")
    mesh = tmp_path / "mesh.txt"
    mesh.write_text("x")
    conn = FakeConn({"cd ": (0, "4711\n")})
    job_id = SlurmClient(conn, profile()).submit_job(str(deck), [str(mesh)], num_procs=4)

    job_dir = f"/home/u/perihub/{job_id}"
    assert conn.files[f"{job_dir}/Dogbone.yaml"] == b"PeriLab: {}"
    assert f"{job_dir}/mesh.txt" in conn.files
    script = conn.files[f"{job_dir}/job.sh"].decode()
    assert "--account=2263032" in script and "--ntasks=4" in script and "--partition" not in script
    assert "--project=/home/u/perilab" in script and '"Dogbone.yaml"' in script
    assert conn.files[f"{job_dir}/slurm_id"] == b"4711"
    assert any("sbatch --parsable" in c for c in conn.commands)


def test_get_job_reads_exit_code_after_squeue_forgets_it():
    conn = FakeConn({"squeue": (0, "")})
    client = SlurmClient(conn, profile())
    job_dir = "/home/u/perihub/" + "a" * 32
    conn.files.update({f"{job_dir}/slurm_id": b"4711", f"{job_dir}/exit_code": b"0\n"})
    assert client.get_job("a" * 32).status == "completed"


def test_delete_job_refuses_paths_outside_workdir():
    conn = FakeConn()
    with pytest.raises(HTTPException) as exc:
        SlurmClient(conn, profile()).delete_job("../x")
    assert exc.value.status_code == 400
    assert conn.commands == []


def test_list_files_hides_bookkeeping_and_download_skips_unchanged(tmp_path):
    conn = FakeConn()
    job_dir = "/home/u/perihub/" + "b" * 32
    for name in ("job.sh", "slurm_id", "exit_code", "perilab.log", "out/Dogbone.e"):
        conn.files[f"{job_dir}/{name}"] = b"data"
    client = SlurmClient(conn, profile())
    assert client.list_files("b" * 32) == ["out/Dogbone.e", "perilab.log"]

    dest = str(tmp_path / "Dogbone.e")
    version = client.download_file("b" * 32, "out/Dogbone.e", dest)
    assert os.path.exists(dest)
    os.remove(dest)
    assert client.download_file("b" * 32, "out/Dogbone.e", dest, known_version=version) == version
    assert not os.path.exists(dest)


def test_host_key_mismatch_is_refused():
    check_host_key(None, "ssh-ed25519 AAA")  # nothing pinned yet: accepted
    check_host_key("ssh-ed25519 AAA", "ssh-ed25519 AAA")
    with pytest.raises(HostKeyMismatch):
        check_host_key("ssh-ed25519 AAA", "ssh-ed25519 BBB")


def test_sftp_errors_become_503_and_calls_are_serialized():
    import threading

    from backend.app.ee.slurm_client import Connection

    class BrokenSftp:
        def stat(self, remote):
            assert conn._lock._is_owned()  # every SFTP call holds the connection's lock
            raise PermissionError("denied")

    conn = Connection.__new__(Connection)
    conn.host, conn._sftp, conn._lock = "cara", BrokenSftp(), threading.RLock()
    with pytest.raises(HTTPException) as exc:
        conn.stat("/x")
    assert exc.value.status_code == 503


def test_default_template_has_the_cara_workarounds():
    assert 'delete!(ENV, "OPAL_PREFIX")' in DEFAULT_TEMPLATE and "exit()" in DEFAULT_TEMPLATE
