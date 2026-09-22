# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Persisted overrides for a subset of the environment-variable configuration
read by support/globals.py, editable from the frontend's Settings dialog.

Design, and why it looks the way it does:

- Everything in globals.py still ultimately comes from ``os.getenv(...)``;
  this module never bypasses that. All it does is *pre-fill*
  ``os.environ`` with previously-saved values, before globals.py reads
  anything, so a saved setting behaves exactly like an env var - except a
  real env var always wins (see ``apply_stored_overrides``).

- A key is "locked" (read-only in the UI) when it is already present in the
  real process environment at the moment globals.py starts (docker
  ``env_file``, ``environment:`` in docker-compose, a real ``.env`` picked
  up by ``load_dotenv()``, ...). That snapshot is taken once, in
  globals.py, as ``ENV_LOCKED_KEYS`` - *before* this module gets a chance to
  inject anything - which is what makes "already defined" and "operator
  configured it outside the app" the same thing.

- Saved overrides live in a small JSON file. Like the audit/usage log paths
  and the license cache path in globals.py, it defaults to somewhere under
  ``backend/app/logs``, which is *not* a volume mounted in
  docker-compose.yml. That means a value saved here currently survives a
  plain container *restart* but not a container being recreated - mount
  ``RUNTIME_SETTINGS_PATH`` (or its parent) if you need it to survive that
  too. This mirrors an existing limitation of this codebase rather than
  introducing a new one.

- Most of support/globals.py's values are read once at import time, and a
  lot of other modules do ``from .globals import some_value`` - a name
  binding taken at *their* import time, not a live reference back into
  globals.py. So changing ``os.environ`` after startup does not ripple
  through the app. A saved change here only takes effect the next time the
  backend process starts; the settings API always reports this back as
  ``restart_required``.
"""

import json
import os
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional


class _SettingDef:
    """One entry in the schema below - metadata for a single env var."""

    def __init__(
        self,
        key: str,
        label: str,
        description: str,
        type_: str,  # "bool" | "int" | "string" | "secret"
        default: str = "",
        choices: Optional[List[str]] = None,
    ):
        self.key = key
        self.label = label
        self.description = description
        self.type = type_
        self.default = default
        self.choices = choices

    @property
    def secret(self) -> bool:
        return self.type == "secret"


# Keep this in the same order as support/globals.py, and keep the `key`
# exactly as the env var name it reads there - the two must line up.
SETTINGS_SCHEMA: List[_SettingDef] = [
    _SettingDef("TRIAL", "Trial mode", "Runs PeriHub with paid features disabled.", "bool", default="False"),
    _SettingDef(
        "DEV",
        "Development mode",
        "Skips the Keycloak login flow and assigns a random guest username instead.",
        "bool",
        default="False",
    ),
    _SettingDef(
        "FRONTMATTER_INSTALLATION",
        "Install own-model requirements",
        "Pip-install the `requirements:` frontmatter of models placed in own_models/ at startup.",
        "bool",
        default="True",
    ),
    _SettingDef(
        "MAX_NODES",
        "Max nodes per model",
        "Upper bound on discretization size for generated models.",
        "int",
        default="50000",
    ),
    _SettingDef(
        "CLUSTER_URL",
        "Cluster URL",
        "SSH host of an external PeriLab cluster. Leave blank to only use the bundled local solver container.",
        "string",
        default="",
    ),
    _SettingDef("CLUSTER_USER", "Cluster user", "SSH username for the cluster.", "string", default=""),
    _SettingDef("CLUSTER_PASSWORD", "Cluster password", "SSH password for the cluster.", "secret", default=""),
    _SettingDef(
        "CLUSTER_JOB_PATH",
        "Cluster job path",
        "Remote path job files are copied to.",
        "string",
        default="./PeridigmJobs/apiModels/",
    ),
    _SettingDef(
        "CLUSTER_PERILAB_PATH", "Cluster PeriLab path", "Remote install path of PeriLab.", "string", default="/PeriLab/"
    ),
    _SettingDef(
        "API_KEYS",
        "API keys",
        'Comma-separated name:key pairs for programmatic/CI callers, e.g. "ci:abc123,partner-x:def456" '
        "(see support/api_key_auth.py).",
        "secret",
        default="",
    ),
    _SettingDef(
        "WS_LOG_WAIT_TIMEOUT_SECONDS",
        "Log-stream wait timeout (s)",
        "How long the /ws log-tail endpoint waits for a job's .log file to appear before giving up.",
        "int",
        default="300",
    ),
    _SettingDef(
        "MAX_CONCURRENT_LOCAL_JOBS",
        "Max concurrent local jobs",
        "In-process concurrency cap on locally-submitted jobs.",
        "int",
        default="4",
    ),
    _SettingDef(
        "SOLVER_BACKEND",
        "Solver backend",
        '"local" runs the bundled perihub_perilab container; "external" points at a customer-hosted '
        "PeriLab server (not functionally complete yet).",
        "string",
        default="local",
        choices=["local", "external"],
    ),
    _SettingDef(
        "EXTERNAL_PERILAB_URL",
        "External PeriLab URL",
        'URL of a customer-hosted PeriLab server, used when the solver backend is "external".',
        "string",
        default="",
    ),
    _SettingDef(
        "LICENSE_SERVER_URL",
        "License server URL",
        "Enables paid-feature gating once set; leave blank to run fully open-core.",
        "string",
        default="",
    ),
    _SettingDef("LICENSE_KEY", "License key", "License key sent to the license server.", "secret", default=""),
    _SettingDef(
        "LICENSE_INSTANCE_ID",
        "License instance ID",
        "Unique id for this PeriHub install, reported to the license server for seat/instance tracking.",
        "string",
        default="",
    ),
    _SettingDef(
        "LICENSE_REFRESH_INTERVAL_SECONDS",
        "License refresh interval (s)",
        "How long a fetched entitlement grant stays valid before it's refreshed from the license server.",
        "int",
        default=str(60 * 60),
    ),
    _SettingDef(
        "LICENSE_OFFLINE_GRACE_PERIOD_SECONDS",
        "License offline grace period (s)",
        "How long last-known-good entitlements are honoured while the license server is unreachable.",
        "int",
        default=str(72 * 60 * 60),
    ),
]

_BY_KEY: Dict[str, _SettingDef] = {field.key: field for field in SETTINGS_SCHEMA}

_DEFAULT_STORE_PATH = Path(__file__).resolve().parent.parent / "logs" / "runtime_settings.json"
settings_store_path = Path(os.getenv("RUNTIME_SETTINGS_PATH", default=str(_DEFAULT_STORE_PATH)))

_lock = Lock()


def _read_store() -> Dict[str, str]:
    try:
        with open(settings_store_path, "r") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_store(data: Dict[str, str]) -> None:
    settings_store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = settings_store_path.with_suffix(".tmp")
    with open(tmp_path, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
    tmp_path.replace(settings_store_path)  # atomic on same filesystem


def _validate(field: _SettingDef, value: str) -> None:
    if field.type == "bool" and value not in ("True", "False"):
        raise ValueError(f'{field.key} must be "True" or "False", got {value!r}')
    if field.type == "int":
        try:
            int(value)
        except ValueError:
            raise ValueError(f"{field.key} must be an integer, got {value!r}")
    if field.choices and value not in field.choices:
        raise ValueError(f"{field.key} must be one of {field.choices}, got {value!r}")


def apply_stored_overrides(already_locked_keys) -> None:
    """Called once from globals.py, before it evaluates any `os.getenv(...)`
    calls, so a previously-saved value is visible to the rest of the app
    exactly like a real env var would be. Keys already present in the real
    environment are left untouched - they always win over a stored value."""
    for key, value in _read_store().items():
        if key not in already_locked_keys:
            os.environ[key] = value


def list_settings(locked_keys) -> List[dict]:
    """Current value + editability of every setting in SETTINGS_SCHEMA.
    `locked_keys` should be `globals.ENV_LOCKED_KEYS`."""
    out = []
    for field in SETTINGS_SCHEMA:
        raw = os.environ.get(field.key, field.default)
        out.append(
            {
                "key": field.key,
                "label": field.label,
                "description": field.description,
                "type": field.type,
                "default": field.default,
                "choices": field.choices,
                "editable": field.key not in locked_keys,
                "is_set": raw not in ("", None),
                # Never echo a secret's actual value back to the client - an
                # empty string here just means "leave it as-is" on save, see
                # update_settings().
                "value": "" if field.secret else raw,
            }
        )
    return out


def update_settings(changes: Dict[str, str], locked_keys) -> None:
    """Validates and persists `changes` (key -> new value). Raises ValueError
    for an unknown key or a value that fails validation, and PermissionError
    for a key that's locked by the real environment. Blank values for
    `secret`-type fields are treated as "no change", not "clear the secret",
    so the frontend can always show a blank input for a secret without
    accidentally wiping it out on an unrelated save."""
    unknown = [key for key in changes if key not in _BY_KEY]
    if unknown:
        raise ValueError(f"Unknown setting(s): {', '.join(sorted(unknown))}")

    locked = [key for key in changes if key in locked_keys]
    if locked:
        raise PermissionError(
            f"These are set via the real environment and can't be edited here: {', '.join(sorted(locked))}"
        )

    with _lock:
        stored = _read_store()
        for key, value in changes.items():
            field = _BY_KEY[key]
            if field.secret and value == "":
                continue
            _validate(field, value)
            stored[key] = value
            os.environ[key] = value  # best-effort: lets a fresh GET reflect it immediately
        _write_store(stored)
