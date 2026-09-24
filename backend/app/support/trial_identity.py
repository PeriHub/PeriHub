# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Random per-session identity for trial mode.

Trial has no persistent accounts (no signup, no password) - each session
just needs an identity distinct from every other concurrent trial user, so
their simulation files/jobs don't collide. Previously `generate_username`
was imported in file_handler.py but never actually called anywhere, so
every trial user with no `userName` header fell back to the same literal
string "user" - the exact collision the roadmap item called out.

This plugs into the existing header-driven identity model rather than
inventing a new one: the frontend calls `POST /auth/trial-id` once per
session and sends the returned username back as the `userName` header on
every subsequent request, exactly like it already does for an OAuth
username today.
"""

import uuid

from random_username.generate import generate_username

from .globals import log


def generate_trial_username() -> str:
    """Returns a fresh, human-readable-ish random username
    ("SwiftFalcon42"-style) with a short uuid suffix to make collisions
    effectively impossible even under concurrent trial signups."""
    try:
        base = generate_username(1)[0]
    except Exception as exc:  # noqa: BLE001 - never let this block trial access
        log.warning("trial_identity: generate_username failed (%s), falling back to uuid", exc)
        base = "TrialUser"
    return f"{base}-{uuid.uuid4().hex[:8]}"
