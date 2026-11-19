"""Slurm cluster client (enterprise): runs a user's PeriHub job on an HPC cluster with their own SSH login.

`SlurmClient` implements the surface of support/perilab_api_client.PeriLabApiClient that the run endpoints use, so
status, log, cancel, delete and result mirroring (support/solver_backend.fetch_external_results) work for cluster runs
unchanged. A PeriLab "job id" here is the uuid of the run's directory under the profile's workdir; the Slurm id lives
in a `slurm_id` file inside it, and the job script writes `exit_code` when PeriLab ends - that file, not `sacct`
(often unavailable or restricted), decides success.

`Connection` is the only paramiko code: SSH for commands, SFTP for files, the host key pinned per profile.
"""

import functools
import io
import os
import posixpath
import re
import shlex
import threading
import time
import uuid
from typing import Iterator, Optional

import paramiko
from fastapi import HTTPException, status

from ..support.globals import log
from ..support.perilab_api_client import PeriLabJob

DEFAULT_TEMPLATE = """#!/bin/bash
#SBATCH --job-name=perihub-{{run}}
#SBATCH --account={{account}}
{{partition_line}}
#SBATCH --ntasks={{num_procs}}
#SBATCH --time={{time_limit}}
#SBATCH --output=perilab.log
cd {{job_dir}}
srun julia --project={{perilab_path}} \\
  -e 'using PeriLab; delete!(ENV, "OPAL_PREFIX"); PeriLab.main(["{{deck}}", "-s"]); exit()'
echo $? > exit_code
"""

#: Files PeriHub writes into a job dir for itself - not results.
_BOOKKEEPING = {"job.sh", "slurm_id", "exit_code"}
_JOB_ID = re.compile(r"[0-9a-f]{32}")
#: How often stream_log looks for new log output.
LOG_POLL_SECONDS = 5


class HostKeyMismatch(Exception):
    pass


def render_template(template: str, values: dict[str, str]) -> str:
    """`{{name}}` placeholders, so bash's own `${VAR}` in a user template is left alone."""
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


def slurm_status(squeue_state: str | None, exit_code: str | None, sacct_state: str | None) -> str:
    """Maps what the cluster tells us onto PeriLab job statuses (perilab_api_client._ACTIVE/_FAILED_JOB_STATUSES)."""
    if squeue_state:
        return "queued" if squeue_state in ("PENDING", "CONFIGURING", "REQUEUED") else "running"
    if exit_code is not None:
        return "completed" if exit_code.strip() == "0" else "failed"
    if sacct_state and sacct_state.startswith("CANCELLED"):
        return "cancelled"
    return "failed"


def check_host_key(pinned: str | None, actual: str) -> None:
    if pinned and pinned != actual:
        raise HostKeyMismatch(f"Host key changed (now {actual[:40]}...) - refusing to connect.")


def _unreachable(host: str, exc: Exception) -> HTTPException:
    log.warning("Cluster %s unreachable: %s", host, exc)
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Cluster {host}: {exc}")


class _PinPolicy(paramiko.MissingHostKeyPolicy):
    """Runs before authentication: a changed host key aborts the connection before our key is ever offered."""

    def __init__(self, pinned: str | None):
        self.pinned = pinned
        self.seen: str | None = None

    def missing_host_key(self, client, hostname, key):
        self.seen = f"{key.get_name()} {key.get_base64()}"
        check_host_key(self.pinned, self.seen)


def _guarded(method):
    """One call at a time per connection (it is shared by the thread-pool requests of one user, and paramiko's SFTP
    client isn't safe for concurrent use); transport/SFTP errors surface as 503 like an offline PeriLab API.
    FileNotFoundError is left to the methods, which treat it as "no such file"."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            try:
                return method(self, *args, **kwargs)
            except FileNotFoundError:
                raise
            except (paramiko.SSHException, OSError) as exc:
                raise _unreachable(self.host, exc) from exc

    return wrapper


class Connection:
    """SSH + SFTP to one cluster login. Errors surface as HTTPException(503), which callers (sync_status, ...) treat
    like an offline PeriLab API."""

    def __init__(self, host: str, port: int, username: str, private_key_pem: str, host_key: str | None):
        self.host = host
        self._lock = threading.RLock()
        self._policy = _PinPolicy(host_key)
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(self._policy)
        try:
            pkey = paramiko.Ed25519Key.from_private_key(io.StringIO(private_key_pem))
            self._ssh.connect(
                host, port=port, username=username, pkey=pkey, timeout=15, allow_agent=False, look_for_keys=False
            )
            self._sftp = self._ssh.open_sftp()
            self._home = self._sftp.normalize(".")
        except HostKeyMismatch as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cluster {host}: {exc}") from exc
        except (paramiko.SSHException, OSError) as exc:
            raise _unreachable(host, exc) from exc

    @property
    def host_key(self) -> str | None:
        """The server's key as seen on this connection (pinned by ee/cluster.py's connection test)."""
        return self._policy.seen

    @property
    def alive(self) -> bool:
        transport = self._ssh.get_transport()
        return transport is not None and transport.is_active()

    def close(self) -> None:
        self._ssh.close()

    def home(self) -> str:
        return self._home

    @_guarded
    def run(self, cmd: str) -> tuple[int, str]:
        _, stdout, stderr = self._ssh.exec_command(cmd, timeout=60)
        out = stdout.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()
        if code:
            out += stderr.read().decode(errors="replace")
        return code, out

    @_guarded
    def put(self, local: str, remote: str) -> None:
        self._sftp.put(local, remote)

    @_guarded
    def write(self, remote: str, data: bytes) -> None:
        with self._sftp.open(remote, "wb") as file:
            file.write(data)

    @_guarded
    def read(self, remote: str) -> bytes | None:
        try:
            with self._sftp.open(remote, "rb") as file:
                return file.read()
        except FileNotFoundError:
            return None

    @_guarded
    def stat(self, remote: str) -> tuple[int, int] | None:
        try:
            attrs = self._sftp.stat(remote)
        except FileNotFoundError:
            return None
        return int(attrs.st_mtime or 0), int(attrs.st_size or 0)

    @_guarded
    def walk(self, root: str) -> list[str]:
        """Relative paths of every file below `root` ([] if it doesn't exist)."""
        out: list[str] = []
        try:
            entries = self._sftp.listdir_attr(root)
        except FileNotFoundError:
            return out
        for entry in entries:
            path = posixpath.join(root, entry.filename)
            if entry.st_mode is not None and entry.st_mode & 0o040000:  # directory
                out += [posixpath.join(entry.filename, sub) for sub in self.walk(path)]
            else:
                out.append(entry.filename)
        return sorted(out)

    @_guarded
    def get(self, remote: str, local: str) -> None:
        self._sftp.get(remote, local)


_connections: dict[tuple, Connection] = {}
_connections_lock = threading.Lock()


def cached_connection(user_id: str, host: str, port: int, username: str, key_pem: str, host_key: str | None):
    """One open connection per user and login - SSH handshakes cost ~1 s and the result views poll.
    ponytail: per-process cache, fine for a single backend worker; a stale entry is replaced on the next call."""
    cache_key = (user_id, host, port, username, key_pem, host_key)
    with _connections_lock:
        conn = _connections.get(cache_key)
        if conn is not None and conn.alive:
            return conn
        for key in [k for k in _connections if k[0] == user_id]:
            _connections.pop(key).close()
        conn = Connection(host, port, username, key_pem, host_key)
        _connections[cache_key] = conn
        return conn


def drop_connections(user_id: str) -> None:
    with _connections_lock:
        for key in [k for k in _connections if k[0] == user_id]:
            _connections.pop(key).close()


class SlurmClient:
    """The PeriLabApiClient methods, answered by the user's cluster. `profile` is a db.models.ClusterProfile (or
    anything with its fields)."""

    def __init__(self, conn, profile):
        self.conn = conn
        self.profile = profile

    # --- paths ----------------------------------------------------------------

    def _expand(self, path: str) -> str:
        for prefix in ("~", "$HOME", "${HOME}"):
            if path == prefix or path.startswith(prefix + "/"):
                return self.conn.home() + path[len(prefix) :]
        return path

    def _workdir(self) -> str:
        return self._expand(self.profile.workdir).rstrip("/")

    def _dir(self, job_id: str) -> str:
        if not _JOB_ID.fullmatch(job_id or ""):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cluster job id.")
        return f"{self._workdir()}/{job_id}"

    def _file(self, job_id: str, name: str) -> str:
        path = posixpath.normpath(posixpath.join(self._dir(job_id), name))
        if not path.startswith(self._dir(job_id) + "/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path.")
        return path

    def _check(self, cmd: str) -> str:
        code, out = self.conn.run(cmd)
        if code:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Cluster: {out.strip()[:500]}")
        return out

    # --- health -----------------------------------------------------------------

    def mpi_available(self) -> bool:
        return True  # srun

    def health(self) -> bool:
        try:
            return self.conn.run("sbatch --version")[0] == 0
        except HTTPException:
            return False

    def version(self) -> str:
        return "slurm"

    # --- jobs -------------------------------------------------------------------

    def submit_job(
        self,
        input_file_path: str,
        extra_file_paths: Optional[list[str]] = None,
        args: str = "",
        num_procs: int = 1,
        user_id: Optional[str] = None,
    ) -> str:
        del args, user_id  # the template decides PeriLab's flags
        job_id = uuid.uuid4().hex
        job_dir = self._dir(job_id)
        self._check(f"mkdir -p {shlex.quote(job_dir)}")
        for local in [input_file_path, *(extra_file_paths or [])]:
            self.conn.put(local, f"{job_dir}/{posixpath.basename(local)}")
        p = self.profile
        script = render_template(
            p.job_template or DEFAULT_TEMPLATE,
            {
                "run": job_id[:8],
                "account": p.account,
                "partition_line": f"#SBATCH --partition={p.partition}" if p.partition else "",
                "num_procs": str(num_procs),
                "time_limit": p.time_limit,
                "job_dir": job_dir,
                "perilab_path": self._expand(p.perilab_path),
                "deck": posixpath.basename(input_file_path),
            },
        )
        self.conn.write(f"{job_dir}/job.sh", script.encode())
        out = self._check(f"cd {shlex.quote(job_dir)} && sbatch --parsable job.sh")
        slurm_id = out.strip().split(";")[0]
        self.conn.write(f"{job_dir}/slurm_id", slurm_id.encode())
        log.info("Cluster job %s submitted as Slurm job %s", job_id, slurm_id)
        return job_id

    def _slurm_id(self, job_id: str) -> str | None:
        data = self.conn.read(f"{self._dir(job_id)}/slurm_id")
        return data.decode().strip() if data else None

    def get_job(self, job_id: str) -> PeriLabJob:
        slurm_id = self._slurm_id(job_id)
        if slurm_id is None:
            return PeriLabJob(job_id=job_id, status="lost", raw={"error": "The cluster job directory is gone"})
        _, squeue = self.conn.run(f"squeue -h -j {shlex.quote(slurm_id)} -o %T")
        squeue = squeue.strip().splitlines()[0] if squeue.strip() else None
        exit_code = sacct = None
        if squeue is None:
            data = self.conn.read(f"{self._dir(job_id)}/exit_code")
            exit_code = data.decode() if data is not None else None
            if exit_code is None:
                code, out = self.conn.run(f"sacct -n -X -P -j {shlex.quote(slurm_id)} -o State")
                sacct = out.strip() if code == 0 and out.strip() else None
        job_status = slurm_status(squeue, exit_code, sacct)
        raw = {"id": job_id, "status": job_status, "slurm_id": slurm_id}
        if job_status == "failed":
            raw["error"] = self.get_log(job_id, tail=5).strip() or f"Slurm job {slurm_id} ended without an exit code"
        return PeriLabJob(job_id=job_id, status=job_status, raw=raw)

    def cancel_job(self, job_id: str) -> None:
        slurm_id = self._slurm_id(job_id)
        if slurm_id:
            self._check(f"scancel {shlex.quote(slurm_id)}")

    def delete_job(self, job_id: str) -> None:
        self._check(f"rm -rf {shlex.quote(self._dir(job_id))}")

    # --- logs -------------------------------------------------------------------

    def get_log(self, job_id: str, tail: Optional[int] = None) -> str:
        data = self.conn.read(f"{self._dir(job_id)}/perilab.log") or b""
        text = data.decode(errors="replace")
        return "\n".join(text.splitlines()[-tail:]) if tail else text

    def stream_log(self, job_id: str) -> Iterator[str]:
        """The log so far, then whatever is appended (polled), until the job is no longer active."""
        path = f"{self._dir(job_id)}/perilab.log"

        def chunks() -> Iterator[str]:
            sent = 0
            while True:
                data = self.conn.read(path) or b""
                if len(data) > sent:
                    yield data[sent:].decode(errors="replace")
                    sent = len(data)
                elif not self.get_job(job_id).is_active:
                    return
                time.sleep(LOG_POLL_SECONDS)

        return chunks()

    # --- result files -------------------------------------------------------------

    def list_files(self, job_id: str) -> list[str]:
        return [name for name in self.conn.walk(self._dir(job_id)) if name not in _BOOKKEEPING]

    def get_file(self, job_id: str, file_path: str) -> bytes:
        data = self.conn.read(self._file(job_id, file_path))
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_path} not found on the cluster")
        return data

    def download_file(self, job_id: str, file_path: str, dest: str, known_version: str | None = None) -> str | None:
        remote = self._file(job_id, file_path)
        stat = self.conn.stat(remote)
        if stat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_path} not found on the cluster")
        version = f"{stat[0]}-{stat[1]}"
        if version == known_version:
            return version
        self.conn.get(remote, dest + ".part")
        os.replace(dest + ".part", dest)  # readers never see a half-written file
        return version
