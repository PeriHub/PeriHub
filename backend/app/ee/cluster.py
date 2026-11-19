"""Slurm cluster jobs with the user's own cluster login (enterprise, "cluster_jobs" feature).

Each user keeps one ClusterProfile: host (must be on the admin's `cluster_allowed_hosts` list - every profile host
is a target this server opens SSH connections to), login, Slurm account, path of their own PeriLab install and an
sbatch template. PeriHub generates the SSH keypair; the user adds the public key to `authorized_keys` on the cluster
and can revoke it there. The private key is stored Fernet-encrypted with a key derived from SESSION_SECRET (rotating
that secret means generating a new key). The host key is pinned by the first successful connection test, and no job
is submitted before that.

Importing this module registers the "cluster" solver with support/solver_backend.py, so the run endpoints reach the
cluster through ee/slurm_client.SlurmClient without core importing ee/.
"""

import base64
import hashlib
import re

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import base
from ..db.base import get_db
from ..db.models import JOB_QUEUED, JOB_RUNNING, ClusterProfile, JobQueueEntry, User
from ..support import audit_log
from ..support.admin_settings import allowed_cluster_hosts
from ..support.entitlements import require_feature
from ..support.globals import session_secret
from ..support.guest import require_non_guest
from ..support.solver_backend import PeriLabSolverBackend, register_solver
from .slurm_client import DEFAULT_TEMPLATE, Connection, SlurmClient, cached_connection, drop_connections

FEATURE = "cluster_jobs"
# What may reach a remote shell or an #SBATCH line unquoted: no quotes, spaces, `;`, `$(`, newlines.
_PLAIN = re.compile(r"^[A-Za-z0-9._@:+-]*$")
_PATH = re.compile(r"^(~|\$HOME|\$\{HOME\})?[A-Za-z0-9._/+-]*$")


def _licensed() -> None:
    require_feature(FEATURE)


router = APIRouter(prefix="/cluster", tags=["Cluster Methods"], dependencies=[Depends(_licensed)])


class ClusterProfileIn(BaseModel):
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(22, ge=1, le=65535)
    username: str = Field(min_length=1, max_length=255)
    account: str = Field(min_length=1, max_length=255)
    perilab_path: str = Field(min_length=1, max_length=1000, description="Julia project of your PeriLab install")
    workdir: str = Field("~/perihub", min_length=1, max_length=1000, description="Remote base folder for runs")
    partition: str = Field("", max_length=255, description="Empty = the cluster's default partition")
    time_limit: str = Field("01:00:00", min_length=1, max_length=32)
    job_template: str | None = Field(None, description="sbatch script with {{placeholders}}; null = the default")

    @field_validator("host", "username", "account", "partition", "time_limit")
    @classmethod
    def _plain(cls, value: str) -> str:
        value = value.strip()
        if not _PLAIN.match(value):
            raise ValueError("letters, digits and . _ @ : + - only")
        return value

    @field_validator("perilab_path", "workdir")
    @classmethod
    def _path(cls, value: str) -> str:
        value = value.strip()
        if not _PATH.match(value) or ".." in value.split("/"):
            raise ValueError("a plain path (may start with ~ or $HOME), no spaces, quotes or ..")
        return value


class ClusterProfileOut(ClusterProfileIn):
    public_key: str | None = Field(None, description="Add this line to ~/.ssh/authorized_keys on the cluster")
    host_key_fingerprint: str | None = Field(None, description="Pinned by the first successful connection test")
    default_job_template: str = Field(DEFAULT_TEMPLATE, description="Used while job_template is null")


class ClusterKey(BaseModel):
    public_key: str


class ClusterTestResult(BaseModel):
    ok: bool
    host_key_fingerprint: str
    sbatch: str
    perilab_found: bool


def _fingerprint(host_key: str | None) -> str | None:
    if not host_key:
        return None
    digest = hashlib.sha256(base64.b64decode(host_key.split()[1])).digest()
    return "SHA256:" + base64.b64encode(digest).decode().rstrip("=")


def _out(row: ClusterProfile) -> ClusterProfileOut:
    fields = {f: getattr(row, f) for f in ClusterProfileIn.model_fields}
    return ClusterProfileOut(**fields, public_key=row.public_key, host_key_fingerprint=_fingerprint(row.host_key))


def _fernet() -> Fernet:
    if not session_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SESSION_SECRET is not set.")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(b"perihub-cluster:" + session_secret.encode()).digest()))


def _check_host(db: Session, host: str) -> None:
    if host.lower() not in allowed_cluster_hosts(db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{host} is not an allowed cluster host.")


def _has_active_runs(db: Session, user_id: str) -> bool:
    active = select(func.count()).where(
        JobQueueEntry.user_id == user_id,
        JobQueueEntry.solver == "cluster",
        JobQueueEntry.status.in_((JOB_QUEUED, JOB_RUNNING)),
    )
    return bool(db.scalar(active))


def _refuse_while_active(db: Session, user_id: str, what: str) -> None:
    if _has_active_runs(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have cluster runs in progress - wait for them or cancel them before {what}.",
        )


def _profile(db: Session, user_id: str) -> ClusterProfile:
    row = db.get(ClusterProfile, user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cluster profile yet.")
    return row


def _private_key(row: ClusterProfile) -> str:
    if not row.private_key_enc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generate an SSH key first.")
    try:
        return _fernet().decrypt(row.private_key_enc.encode()).decode()
    except InvalidToken as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The stored SSH key can't be decrypted (SESSION_SECRET changed?) - generate a new one.",
        ) from exc


@router.get("/profile", operation_id="get_cluster_profile")
def get_cluster_profile(user: User = Depends(require_non_guest), db: Session = Depends(get_db)) -> ClusterProfileOut:
    """The caller's cluster profile (never the private key); 404 if they have none."""
    return _out(_profile(db, user.id))


@router.put("/profile", operation_id="save_cluster_profile")
def save_cluster_profile(
    payload: ClusterProfileIn,
    request: Request,
    user: User = Depends(require_non_guest),
    db: Session = Depends(get_db),
) -> ClusterProfileOut:
    """Create or update the caller's cluster profile. 400 if the host isn't on the admin's allow-list; 409 when the
    login or workdir would change while cluster runs are in progress (they'd become unreachable)."""
    _check_host(db, payload.host)
    row = db.get(ClusterProfile, user.id)
    if row is None:
        row = ClusterProfile(user_id=user.id)
        db.add(row)
    else:
        login = ("host", "port", "username", "workdir")
        if any(getattr(row, f) != getattr(payload, f) for f in login):
            _refuse_while_active(db, user.id, "changing the login or workdir")
        if (row.host, row.port) != (payload.host, payload.port):
            row.host_key = None  # a different server: pin again on the next test
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    drop_connections(user.id)
    audit_log.record(user.id, "save_cluster_profile", payload.host, request)
    return _out(row)


@router.delete("/profile", operation_id="delete_cluster_profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_cluster_profile(
    request: Request, user: User = Depends(require_non_guest), db: Session = Depends(get_db)
) -> Response:
    """Delete the caller's cluster profile and key. 409 while cluster runs are in progress."""
    row = _profile(db, user.id)
    _refuse_while_active(db, user.id, "deleting the profile")
    db.delete(row)
    db.commit()
    drop_connections(user.id)
    audit_log.record(user.id, "delete_cluster_profile", row.host, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/profile/key", operation_id="generate_cluster_key")
def generate_cluster_key(
    request: Request, user: User = Depends(require_non_guest), db: Session = Depends(get_db)
) -> ClusterKey:
    """Generate a new ed25519 keypair for the caller's profile, replacing the old one, and return the public key to
    add to ~/.ssh/authorized_keys on the cluster. 409 while cluster runs are in progress."""
    row = _profile(db, user.id)
    _refuse_while_active(db, user.id, "replacing the key")
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.OpenSSH, serialization.NoEncryption()
    )
    public = key.public_key().public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)
    row.private_key_enc = _fernet().encrypt(pem).decode()
    row.public_key = f"{public.decode()} perihub-{user.id[:8]}"
    db.commit()
    drop_connections(user.id)
    audit_log.record(user.id, "generate_cluster_key", row.host, request)
    return ClusterKey(public_key=row.public_key)


@router.post("/profile/test", operation_id="test_cluster_connection")
def test_cluster_connection(
    user: User = Depends(require_non_guest), db: Session = Depends(get_db)
) -> ClusterTestResult:
    """Log in to the cluster with the caller's key, pin its host key on the first success, and check that `sbatch`
    works and `perilab_path` exists. 503 when the cluster can't be reached or the key isn't authorized, 409 when its
    host key changed since it was pinned."""
    row = _profile(db, user.id)
    _check_host(db, row.host)
    conn = Connection(row.host, row.port, row.username, _private_key(row), row.host_key)
    try:
        code, sbatch = conn.run("sbatch --version")
        perilab = SlurmClient(conn, row)._expand(row.perilab_path)
        perilab_found = conn.stat(perilab) is not None
    finally:
        conn.close()
    if row.host_key is None:
        row.host_key = conn.host_key
        db.commit()
    return ClusterTestResult(
        ok=code == 0 and perilab_found,
        host_key_fingerprint=_fingerprint(row.host_key) or "",
        sbatch=sbatch.strip()[:200],
        perilab_found=perilab_found,
    )


def _cluster_backend(user_id: str | None) -> PeriLabSolverBackend:
    """solver_backend factory for "cluster": the run owner's own profile, re-checked against licence and allow-list
    on every use."""
    require_feature(FEATURE)
    if user_id is None or base.SessionLocal is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cluster runs need a logged-in account.")
    with base.SessionLocal() as db:
        row = db.get(ClusterProfile, user_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Set up a cluster profile first.")
        _check_host(db, row.host)
        if row.host_key is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Test the cluster connection in your settings first."
            )
        key = _private_key(row)
        db.expunge(row)
    conn = cached_connection(user_id, row.host, row.port, row.username, key, row.host_key)
    return PeriLabSolverBackend("", shares_local_filesystem=False, client=SlurmClient(conn, row))


register_solver("cluster", _cluster_backend)
