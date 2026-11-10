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

import json
import os
import shutil
import time

from ..db import base
from . import gcode_mesh_cache
from .admin_settings import instance_setting
from .deck_guard import check_input_deck
from .file_handler import FileHandler, safe_segment
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
        input_file_paths = [
            os.path.join(remotepath, f"{model_name}.yaml" if jid == "-1" else f"{model_name}_{safe_segment(jid)}.yaml")
            for jid in variants
        ]
        # Every deck is checked before any is submitted, so a rejected batch leaves no PeriLab jobs behind.
        for input_file_path in input_file_paths:
            check_input_deck(input_file_path)
            gcode_mesh_cache.drop_if_stale(remotepath, input_file_path)
        job_ids_submitted = []
        for input_file_path in input_file_paths:
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


def _external_perilab_url() -> str:
    """Admin-page override (admin_settings) if a DB is configured, else the env var."""
    if base.SessionLocal is None:
        return external_perilab_url
    with base.SessionLocal() as db:
        return instance_setting(db, "external_perilab_url")


#: A running external job is re-synced at most this often, however often the result views poll.
EXTERNAL_REFRESH_SECONDS = 30


def result_cache_dir(job_id: str) -> str:
    """Local copy of an external run's output (the local solver writes straight to simulations/<job_id>/)."""
    return os.path.join(FileHandler.get_local_simulation_path(), "_external", safe_segment(job_id))


def _state_path(job_id: str) -> str:
    # Next to the folder, not in it, so it never ends up in the result zip.
    return result_cache_dir(job_id) + ".json"


def fetch_external_results(
    client: PeriLabApiClient,
    job_id: str,
    finished: bool,
    folder: str | None = None,
    state_path: str | None = None,
    keep=None,
) -> str:
    """Mirrors an external PeriLab job's files into result_cache_dir (or `folder`), so the results endpoints can read
    them like a local run's. Keeps traffic down: a finished run is synced once and then served from disk, a running
    one at most every EXTERNAL_REFRESH_SECONDS, and a file whose ETag hasn't changed is never downloaded again.
    `keep(name)` filters which files are mirrored."""
    folder = folder or result_cache_dir(job_id)
    state_path = state_path or _state_path(job_id)
    try:
        with open(state_path) as file:
            state = json.load(file)
    except (OSError, json.JSONDecodeError):
        state = {"versions": {}, "fetched_at": 0, "complete": False}
    if state["complete"] or (not finished and time.time() - state["fetched_at"] < EXTERNAL_REFRESH_SECONDS):
        return folder

    root = os.path.realpath(folder)
    versions = state["versions"]
    for name in client.list_files(job_id):
        if keep is not None and not keep(name):
            continue
        dest = os.path.realpath(os.path.join(folder, name))
        if not dest.startswith(root + os.sep):  # the external server is not trusted with our filesystem
            log.warning("Skipping result file outside the job folder: %s", name)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        known = versions.get(name) if os.path.exists(dest) else None
        versions[name] = client.download_file(job_id, name, dest, known_version=known)
    state.update(fetched_at=time.time(), complete=finished)
    os.makedirs(os.path.dirname(folder), exist_ok=True)
    with open(state_path, "w") as file:
        json.dump(state, file)
    return folder


def drop_result_cache(job_id: str) -> None:
    shutil.rmtree(result_cache_dir(job_id), ignore_errors=True)
    if os.path.exists(_state_path(job_id)):
        os.remove(_state_path(job_id))


def run_result_dir(run_id: str) -> str:
    """One folder per batch run (deviation samples), holding every job's output side by side - the layout analyses
    expect (`<model>_<output>_<n>.csv` next to `<model>_deviations.json`)."""
    return os.path.join(FileHandler.get_local_simulation_path(), "_runs", safe_segment(run_id))


def collect_batch_results(backend: SolverBackend, run_id: str, job_ids: list[str], variants: list[str], finished: bool):
    """Merges the jobs of a batch run into run_result_dir. Output names are unique per variant ("_<n>" suffix) and the
    shared inputs (mesh, deviations JSON) are identical in every job, so the first copy of a name wins. Local jobs are
    symlinked from the shared volume; external ones are downloaded, but only the default deck's ("-1") Exodus file:
    one per sample would be ~20 MB each. ponytail: sample Exodus files can't be viewed then - fetch on demand if
    needed."""
    folder = run_result_dir(run_id)
    os.makedirs(folder, exist_ok=True)
    for job_id, variant in zip(job_ids, variants):
        if backend.shares_local_filesystem:
            source = os.path.join(FileHandler.get_local_simulation_path(), safe_segment(job_id))
            for name in os.listdir(source) if os.path.isdir(source) else []:
                link = os.path.join(folder, name)
                if not os.path.lexists(link):
                    os.symlink(os.path.relpath(os.path.join(source, name), folder), link)
        else:
            state_path = f"{folder}.{job_id}.json"
            try:
                with open(state_path) as file:
                    owned = set(json.load(file)["versions"])
            except (OSError, json.JSONDecodeError, KeyError):
                owned = set()

            def keep(name, owned=owned, variant=variant):
                if variant != "-1" and name.endswith(".e"):
                    return False
                # A shared input another job already brought along isn't downloaded again.
                return name in owned or not os.path.exists(os.path.join(folder, name))

            fetch_external_results(backend.client(), job_id, finished, folder, state_path, keep)
    return folder


def drop_run_results(run_id: str) -> None:
    folder = run_result_dir(run_id)
    shutil.rmtree(folder, ignore_errors=True)
    parent = os.path.dirname(folder)
    for name in os.listdir(parent) if os.path.isdir(parent) else []:
        if name.startswith(os.path.basename(folder) + ".") and name.endswith(".json"):
            os.remove(os.path.join(parent, name))


def external_available() -> bool:
    return bool(_external_perilab_url())


def default_solver() -> str:
    """What the frontend preselects: SOLVER_BACKEND, if that server is usable."""
    return "external" if solver_backend_kind == "external" and external_available() else "local"


def get_solver_backend(solver: str | None = None) -> SolverBackend:
    """The PeriLab API a run talks to. Each run stores the server it was submitted to
    (JobQueueEntry.solver) and passes it here; None means the default (SOLVER_BACKEND)."""
    if (solver or default_solver()) == "external":
        url = _external_perilab_url()
        if url:
            return PeriLabSolverBackend(url, shares_local_filesystem=False)
        log.warning("External PeriLab requested but EXTERNAL_PERILAB_URL is not set; falling back to local")
    return PeriLabSolverBackend(local_perilab_api_url, shares_local_filesystem=True)
