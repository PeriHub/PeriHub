# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Usage metering: records job submissions/cancellations as JSON lines and
aggregates them into a UsageSummary on read.

Deliberately append-only-file-based (like support/audit_log.py) rather than
a database - this is meant for basic "how much is this instance being used"
visibility (e.g. to justify a support/instance-sizing conversation, or for a
future usage-based billing tier), not as a system of record. If usage data
needs to survive log rotation/be queried at scale, this is the place to swap
in a real datastore without changing the UsageSummary contract the frontend
already depends on (GET /usage/me, GET /usage/all).
"""

import json
import os
import threading
from datetime import datetime, timezone
from typing import Optional

from .base_models import UsageSummary
from .globals import log, usage_log_path

_lock = threading.Lock()


def _append(entry: dict) -> None:
    try:
        os.makedirs(os.path.dirname(usage_log_path), exist_ok=True)
        with _lock:
            with open(usage_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    except OSError as exc:
        log.warning("usage_metering: failed to write entry: %s", exc)


def record_job_submission(
    username: str,
    model_name: str,
    model_folder_name: str,
    cluster: Optional[str],
    sbatch: bool,
    node_count: Optional[int] = None,
) -> None:
    _append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "submitted",
            "username": username,
            "model_name": model_name,
            "model_folder_name": model_folder_name,
            "cluster": bool(cluster),
            "sbatch": sbatch,
            "node_count": node_count,
        }
    )


def record_job_cancellation(
    username: str, model_name: str, model_folder_name: str, cluster: Optional[str]
) -> None:
    _append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "cancelled",
            "username": username,
            "model_name": model_name,
            "model_folder_name": model_folder_name,
            "cluster": bool(cluster),
        }
    )


def _read_entries() -> list[dict]:
    if not os.path.exists(usage_log_path):
        return []
    entries = []
    with open(usage_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # tolerate a partially-written last line
    return entries


def _summarize(entries: list[dict]) -> UsageSummary:
    jobs_per_user: dict[str, int] = {}
    jobs_per_model: dict[str, int] = {}
    submitted = 0
    cancelled = 0
    cluster_jobs = 0
    local_jobs = 0

    for entry in entries:
        if entry.get("event") == "submitted":
            submitted += 1
            username = entry.get("username", "unknown")
            model_name = entry.get("model_name", "unknown")
            jobs_per_user[username] = jobs_per_user.get(username, 0) + 1
            jobs_per_model[model_name] = jobs_per_model.get(model_name, 0) + 1
            if entry.get("cluster"):
                cluster_jobs += 1
            else:
                local_jobs += 1
        elif entry.get("event") == "cancelled":
            cancelled += 1

    return UsageSummary(
        total_jobs_submitted=submitted,
        total_jobs_cancelled=cancelled,
        cluster_jobs=cluster_jobs,
        local_jobs=local_jobs,
        jobs_per_user=jobs_per_user,
        jobs_per_model=jobs_per_model,
    )


def get_usage_for_user(username: str) -> UsageSummary:
    entries = [e for e in _read_entries() if e.get("username") == username]
    return _summarize(entries)


def get_all_usage() -> UsageSummary:
    return _summarize(_read_entries())
