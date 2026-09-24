# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Caps how many locally-submitted (non-cluster) jobs can run at once.

Local jobs all run through the PeriLab API (support/perilab_api_client.py) -
either the bundled container or an external instance - so without a limit,
submitting N models at once just piles all N onto it with no queuing. This
is a stop-gap against that, not a real job queue. Cluster/sbatch
submissions go to Slurm instead, which already queues on its own, so
they're intentionally not subject to this cap.

Activity used to be detected by scanning for `pid.txt` files - that was the
one thing PeriHub's own filesystem could see about a job it launched via
`docker exec`. Now that jobs are submitted to the PeriLab API and tracked
via JobQueueEntry.perilab_job_id (support/job_queue.py), "how many are
active" is a DB query instead - which is also why local (non-cluster) job
submission now requires DATABASE_URL to be configured (see
support/solver_backend.py's module docstring).
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models import JOB_RUNNING, JobQueueEntry
from .globals import max_concurrent_local_jobs


def count_active_local_jobs(db: Session) -> int:
    """Counts JobQueueEntry rows currently RUNNING (i.e. submitted to the
    PeriLab API and not yet finished/failed/cancelled)."""
    return db.scalar(select(func.count()).select_from(JobQueueEntry).where(JobQueueEntry.status == JOB_RUNNING)) or 0


def has_capacity(db: Session) -> bool:
    """True if another local job can be accepted right now."""
    return count_active_local_jobs(db) < max_concurrent_local_jobs
