# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Append-only audit log for security-sensitive actions.

This intentionally writes plain JSON lines to a local file rather than a
database or external SIEM - it's meant as a minimal, dependency-free starting
point that's easy to ship logs from (e.g. via a log-forwarding sidecar) once
a real deployment needs one. Not a replacement for a proper audit trail with
tamper-evidence guarantees if that's ever a requirement.
"""

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import Request

from .globals import audit_log_path, log

_lock = threading.Lock()


def record(
    username: str,
    action: str,
    target: str,
    request: Optional[Request] = None,
    extra: Optional[dict[str, Any]] = None,
    result: str = "ok",
) -> None:
    """Append one audit entry. Never raises - a logging failure should not
    take down the request it's trying to audit."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "action": action,
        "target": target,
        "result": result,
        "client_host": request.client.host if request is not None and request.client else None,
    }
    if extra:
        entry["extra"] = extra

    try:
        os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)
        with _lock:
            with open(audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    except OSError as exc:
        log.warning("audit_log: failed to write entry (%s): %s", action, exc)
