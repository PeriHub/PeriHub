# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Pluggable solver-backend abstraction.

routers/jobs.py used to hand-roll two *separate* SSH-connect-with-
localhost-fallback implementations - one inline in `run_model` (via
FileHandler.ssh_to_perilab) and a second, subtly different one duplicated
inline in `cancel_job` (its own paramiko.SSHClient() + manual
gaierror/localhost retry loop). This consolidates both call sites onto one
implementation (LocalSolverBackend, itself just a thin wrapper around the
existing FileHandler.ssh_to_perilab()) and gives the run/cancel call sites a
single interface to depend on.

That interface is also the seam for the planned "point PeriHub at a
customer-hosted PeriLab server" enterprise feature (ExternalSolverBackend):
gated via support/entitlements.py, not implemented here - see the
NotImplementedError below and the roadmap.
"""

import os

from .file_handler import FileHandler
from .globals import external_perilab_url, log, solver_backend_kind


class SolverBackend:
    """Interface both backends implement."""

    def submit(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        raise NotImplementedError

    def cancel(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        raise NotImplementedError


class LocalSolverBackend(SolverBackend):
    """Talks to the bundled `perihub_perilab` docker container over SSH -
    the only backend PeriHub actually runs jobs through today."""

    def submit(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        ssh = FileHandler.ssh_to_perilab()
        command = (
            "cd /app"
            + "/simulations/"
            + os.path.join(username, model_name, model_folder_name)
            + " \n sh runPerilab.sh > /dev/null 2>&1 &"
        )
        ssh.exec_command(command)
        ssh.close()

    def cancel(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        del username, model_name, model_folder_name  # only remotepath is needed for the kill command
        ssh = FileHandler.ssh_to_perilab()
        command = (
            "kill -2 $(cat /app" + os.path.join(remotepath, "pid.txt") + ") \n rm /app" + os.path.join(remotepath, "pid.txt")
        )
        ssh.exec_command(command)
        ssh.close()


class ExternalSolverBackend(SolverBackend):
    """Placeholder for the planned enterprise feature of running against a
    customer-hosted PeriLab server instead of the bundled container.

    NOT functionally complete: PeriHub has no documented protocol yet for
    submitting/cancelling jobs against an arbitrary remote PeriLab HTTP(S)
    endpoint (auth, payload shape, job-id correlation for later status/log
    polling are all still open questions). Raising clearly here is
    intentional so a misconfigured SOLVER_BACKEND=external fails loudly
    instead of silently doing nothing.
    """

    def __init__(self, url: str):
        self.url = url

    def submit(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        raise NotImplementedError(
            "SOLVER_BACKEND=external is not implemented yet - "
            f"EXTERNAL_PERILAB_URL={self.url!r} is configured but there is no client for it. "
            "See support/solver_backend.py."
        )

    def cancel(self, username: str, model_name: str, model_folder_name: str, remotepath: str) -> None:
        raise NotImplementedError(
            "SOLVER_BACKEND=external is not implemented yet - see support/solver_backend.py."
        )


def get_solver_backend() -> SolverBackend:
    if solver_backend_kind == "external":
        if not external_perilab_url:
            log.warning("SOLVER_BACKEND=external but EXTERNAL_PERILAB_URL is not set; falling back to local")
            return LocalSolverBackend()
        return ExternalSolverBackend(external_perilab_url)
    return LocalSolverBackend()
