# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Solver backend seam.

routers/jobs.py used to submit/cancel local jobs by running commands
directly inside the bundled `perihub_perilab` docker container via
FileHandler.get_perilab_container() (Docker Engine API `exec`). That's
gone now: both the bundled container and a customer-hosted server are
reached the same way, over the PeriLab HTTP API (support/perilab_api_client.py,
see project root openapi.json) - "local" vs "external" (SOLVER_BACKEND env
var) only changes which URL is used and whether result/log files can be
read straight off the shared docker volume or have to be downloaded
through the API. See support/job_queue.py for how the returned job_id is
persisted (JobQueueEntry.perilab_job_id) so later status/log/cancel calls
know which PeriLab job to ask about - this requires DATABASE_URL to be
configured; local (non-cluster) job submission is no longer supported
without a database, since there is no longer a pid.txt-style filesystem
signal to fall back on.
"""

import os

from .globals import (
    external_perilab_url,
    local_perilab_api_url,
    log,
    solver_backend_kind,
)
from .perilab_api_client import PeriLabApiClient


class SolverBackend:
    """Interface both backends implement. `submit` returns the PeriLab
    job_id (or several, comma-separated - see PeriLabSolverBackend.submit),
    which callers (support/job_queue.py) are responsible for persisting -
    this module has no storage of its own."""

    #: True for the bundled local container, which shares docker-compose's
    #: `perihub` volume with perihub_backend (see docker-stack-extern.yml) -
    #: so result/log files can be read directly off disk at the same
    #: `remotepath` PeriHub already uses, instead of downloaded through the
    #: API. False for a remote/external PeriLab API with no shared disk.
    shares_local_filesystem: bool = False

    def submit(
        self,
        username: str,
        model_name: str,
        model_folder_name: str,
        remotepath: str,
        args: str = "",
        num_procs: int = 1,
        job_ids: str = "-1",
    ) -> str:
        """Submits the model already written to `remotepath` (see
        FileHandler.get_local_model_folder_path) and returns the PeriLab
        job_id (or comma-separated job_ids - see PeriLabSolverBackend.submit)."""
        raise NotImplementedError

    def cancel(self, perilab_job_id: str) -> None:
        raise NotImplementedError

    def client(self) -> PeriLabApiClient:
        raise NotImplementedError


class PeriLabSolverBackend(SolverBackend):
    """Talks to a PeriLab API instance - either the bundled local container
    or a customer-hosted external one, depending on `base_url`."""

    def __init__(self, base_url: str, shares_local_filesystem: bool):
        self._client = PeriLabApiClient(base_url)
        self.shares_local_filesystem = shares_local_filesystem

    def client(self) -> PeriLabApiClient:
        return self._client

    def submit(
        self,
        username: str,
        model_name: str,
        model_folder_name: str,
        remotepath: str,
        args: str = "",
        num_procs: int = 1,
        job_ids: str = "-1",
    ) -> str:
        del username  # folder identity only, not needed once files live under remotepath

        # PeriHub's old shell-script runner could launch several
        # "<model>_<job_id>.yaml" variants back to back from one
        # submission (see support/writer/sbatch_writer.py's job_ids
        # handling) - the PeriLab API only takes one input_file per
        # submission, so mirror that by submitting each variant
        # separately. The single (non-batch) case is job_ids="-1".
        variants = [jid for jid in (job_ids or "-1").split(",")]
        job_ids_submitted = []
        for jid in variants:
            filename = f"{model_name}.yaml" if jid == "-1" else f"{model_name}_{jid}.yaml"
            input_file_path = os.path.join(remotepath, filename)
            extra_files = [
                os.path.join(remotepath, f)
                for f in os.listdir(remotepath)
                if os.path.join(remotepath, f) != input_file_path and os.path.isfile(os.path.join(remotepath, f))
            ]
            job_id = self._client.submit_job(
                input_file_path=input_file_path,
                extra_file_paths=extra_files,
                args=args,
                num_procs=num_procs,
            )
            job_ids_submitted.append(job_id)

        # Multiple variants -> caller (support/job_queue.py) stores a
        # comma-separated list, same convention job_ids itself already uses.
        return ",".join(job_ids_submitted)

    def cancel(self, perilab_job_id: str) -> None:
        for job_id in perilab_job_id.split(","):
            job_id = job_id.strip()
            if job_id:
                self._client.cancel_job(job_id)


def get_solver_backend() -> SolverBackend:
    if solver_backend_kind == "external":
        if not external_perilab_url:
            log.warning("SOLVER_BACKEND=external but EXTERNAL_PERILAB_URL is not set; falling back to local")
            return PeriLabSolverBackend(local_perilab_api_url, shares_local_filesystem=True)
        return PeriLabSolverBackend(external_perilab_url, shares_local_filesystem=False)
    return PeriLabSolverBackend(local_perilab_api_url, shares_local_filesystem=True)
