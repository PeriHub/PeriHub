# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Caps how many locally-submitted (non-cluster) jobs can run at once.

Local jobs all run inside the single bundled `perihub_perilab` container, so
without a limit, submitting N models at once just piles all N onto that one
container with no queuing - this is a stop-gap against that, not a real job
queue. Cluster/sbatch submissions go to Slurm instead, which already queues
on its own, so they're intentionally not subject to this cap.

Activity is detected the same way `jobs.py` already does elsewhere: the
presence of a `pid.txt` file in a model-folder's local simulation directory
means PeriLab is (or very recently was) running there - see
support/writer/sbatch_writer.py, which writes it, and the existing
`if os.path.exists(os.path.join(remotepath, "pid.txt"))` checks in
routers/jobs.py. Scanning the filesystem like this is intentionally simple
and stateless (survives a backend restart without needing its own
persistence) rather than tracking submitted jobs in an in-memory registry
that a restart would silently lose track of.
"""

import os

from .file_handler import FileHandler
from .globals import max_concurrent_local_jobs


def count_active_local_jobs() -> int:
    """Counts model-folders under the local simulations root that currently
    have a pid.txt (i.e. are actively running, per the existing convention
    used elsewhere in routers/jobs.py)."""
    root = FileHandler.get_local_simulation_path()
    count = 0
    for user_dir in _safe_listdir(root):
        user_path = os.path.join(root, user_dir)
        if not os.path.isdir(user_path):
            continue
        for model_dir in _safe_listdir(user_path):
            model_path = os.path.join(user_path, model_dir)
            if not os.path.isdir(model_path):
                continue
            for folder_dir in _safe_listdir(model_path):
                folder_path = os.path.join(model_path, folder_dir)
                if os.path.isfile(os.path.join(folder_path, "pid.txt")):
                    count += 1
    return count


def has_capacity() -> bool:
    """True if another local job can be accepted right now."""
    return count_active_local_jobs() < max_concurrent_local_jobs


def _safe_listdir(path: str) -> list[str]:
    try:
        return os.listdir(path)
    except OSError:
        return []
