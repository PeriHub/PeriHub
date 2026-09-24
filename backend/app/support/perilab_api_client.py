# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Thin client for the PeriLab Simulation API (see project root
`openapi.json`).

This replaces two things PeriHub used to do itself for non-cluster jobs:
    - running PeriLab via `docker exec` inside the bundled perihub_perilab
      container (support/solver_backend.py's old LocalSolverBackend)
    - the never-finished "customer-hosted PeriLab server" placeholder
      (ExternalSolverBackend)

Both are now the same PeriLab API, just reachable at a different URL and
(for "local") sharing a docker volume with this container - see
support/solver_backend.py for how the two are told apart.

NOTE ON RESPONSE SHAPES: field names below are taken from the PeriLab API's
own `Job.to_dict()` (see its support/jobs.py): a job is serialized as `id`,
`status` (one of "queued"/"running"/"completed"/"failed"/"cancelled"/
"interrupted"), `exit_code`, `error`, `created_at`, `started_at`,
`finished_at`, `user_id`, `step`, `total_steps`, `sim_time`, and `progress`
(a 0-1 fraction, present only once `step`/`total_steps` are known - see
`Job.progress`). `PeriLabJob.raw` always keeps the untouched response dict
so callers/log output can fall back to it if the real API ever changes shape.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, BinaryIO, Optional

import requests
from fastapi import HTTPException, status

from .globals import log, perilab_api_timeout_seconds

# Exact statuses the PeriLab API's JobStatus enum uses (support/jobs.py).
# "completed" is neither active nor failed - it's the success terminal state.
_ACTIVE_JOB_STATUSES = {"queued", "running"}
_FAILED_JOB_STATUSES = {"failed", "cancelled", "interrupted"}


class PeriLabApiError(RuntimeError):
    """Raised when the PeriLab API can't be reached or returns an error."""


@dataclass
class PeriLabJob:
    """Normalized view of a GET /jobs/{job_id} response."""

    job_id: str
    status: str
    raw: dict = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.status.lower() in _ACTIVE_JOB_STATUSES

    @property
    def is_failed(self) -> bool:
        return self.status.lower() in _FAILED_JOB_STATUSES

    @property
    def progress(self) -> Optional[float]:
        """0-1 fraction (Job.progress); absent until `step`/`total_steps`
        are both known, i.e. before PeriLab's own log file appears."""
        return self.raw.get("progress")

    @property
    def current_step(self) -> Optional[int]:
        return self.raw.get("step")

    @property
    def total_steps(self) -> Optional[int]:
        return self.raw.get("total_steps")


class PeriLabApiClient:
    """One instance per base URL (local bundled container, or an external
    customer-hosted server - see support/solver_backend.py)."""

    def __init__(self, base_url: str, timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout if timeout is not None else perilab_api_timeout_seconds

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        try:
            response = requests.request(method, self._url(path), **kwargs)
        except requests.RequestException as exc:
            log.error("PeriLab API %s %s failed: %s", method, path, exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not reach the PeriLab API at {self.base_url}: {exc}",
            ) from exc
        if response.status_code >= 400:
            log.error(
                "PeriLab API %s %s -> %s: %s",
                method,
                path,
                response.status_code,
                response.text[:500],
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"PeriLab API returned {response.status_code} for {path}: {response.text[:500]}",
            )
        return response

    # --- /health, /version --------------------------------------------------

    def health(self) -> bool:
        try:
            self._request("GET", "/health")
            return True
        except HTTPException:
            return False

    def version(self) -> str:
        """Returns the PeriLab version string the API serves, or "unknown"
        if the field isn't where expected (see module docstring)."""
        data = self._request("GET", "/version").json()
        if isinstance(data, dict):
            return str(data.get("version", data.get("perilab_version", "unknown")))
        return str(data)

    # --- job submission -------------------------------------------------------

    def submit_job(
        self,
        input_file_path: str,
        extra_file_paths: Optional[list[str]] = None,
        args: str = "",
        num_procs: int = 1,
        user_id: Optional[str] = None,
    ) -> str:
        """POSTs the YAML input deck plus any mesh/auxiliary files to
        /jobs, matching Body_submit_job_jobs_post exactly. Returns the new
        job's id.

        Used as-is for the external (no shared volume) backend, and also
        for the local/bundled backend for now - see
        support/solver_backend.py's PeriLabSolverBackend docstring for why
        the local case still uploads rather than passing a path, even
        though perihub_backend and the bundled perilab container share a
        volume (`perihub:/app/simulations` in docker-stack-extern.yml):
        the API as specified only accepts multipart uploads, with no
        "read this path I already have mounted" option. If the PeriLab API
        gains such an option (e.g. an optional `working_dir` form field
        that skips `input_file`/`extra_files` when set), the local
        backend should use it instead to skip re-uploading files that are
        already on disk in both containers.
        """
        extra_file_paths = extra_file_paths or []
        opened: list[BinaryIO] = []
        try:
            files = []
            input_fh = open(input_file_path, "rb")
            opened.append(input_fh)
            files.append(("input_file", (os.path.basename(input_file_path), input_fh)))
            for extra_path in extra_file_paths:
                fh = open(extra_path, "rb")
                opened.append(fh)
                files.append(("extra_files", (os.path.basename(extra_path), fh)))

            data = {"args": args, "num_procs": str(num_procs)}
            if user_id is not None:
                data["user_id"] = user_id

            response = self._request("POST", "/jobs", files=files, data=data)
        finally:
            for fh in opened:
                fh.close()

        payload = response.json()
        job_id = payload.get("job_id") or payload.get("id") if isinstance(payload, dict) else None
        if not job_id:
            raise PeriLabApiError(f"PeriLab API did not return a job_id from POST /jobs: {payload!r}")
        return str(job_id)

    # --- job control / status --------------------------------------------------

    def get_job(self, job_id: str) -> PeriLabJob:
        payload = self._request("GET", f"/jobs/{job_id}").json()
        if not isinstance(payload, dict):
            payload = {}
        job_status = str(payload.get("status", payload.get("state", "unknown")))
        return PeriLabJob(job_id=job_id, status=job_status, raw=payload)

    def list_jobs(self, user_id: Optional[str] = None) -> list[dict]:
        params = {"user_id": user_id} if user_id else None
        payload = self._request("GET", "/jobs", params=params).json()
        return payload if isinstance(payload, list) else payload.get("jobs", [])

    def cancel_job(self, job_id: str) -> None:
        self._request("POST", f"/jobs/{job_id}/cancel")

    def delete_job(self, job_id: str) -> None:
        self._request("DELETE", f"/jobs/{job_id}")

    # --- logs -------------------------------------------------------------------

    def get_log(self, job_id: str, tail: Optional[int] = None) -> str:
        params = {"tail": tail} if tail else None
        response = self._request("GET", f"/jobs/{job_id}/log", params=params)
        return response.text

    # /jobs/{job_id}/log/stream (server-sent events) is a natural fit for
    # the frontend's /ws endpoint, but that endpoint currently just polls
    # GET /log on a timer for the cluster case too - streaming support can
    # be added here (using requests' streaming mode) if/when /ws is
    # switched over to it for the "external" backend.

    # --- result files -------------------------------------------------------------

    def list_files(self, job_id: str) -> list[str]:
        payload = self._request("GET", f"/jobs/{job_id}/files").json()
        if isinstance(payload, list):
            return payload
        return payload.get("files", [])

    def download_file(self, job_id: str, file_path: str, destination_path: str) -> None:
        response = self._request("GET", f"/jobs/{job_id}/files/{file_path}", stream=True)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                f.write(chunk)
