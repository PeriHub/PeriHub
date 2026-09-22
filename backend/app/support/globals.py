# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os

from dotenv import load_dotenv
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(level=logging.INFO)],
)
logging.getLogger("paramiko").setLevel(logging.WARNING)

log = logging.getLogger("rich")

load_dotenv()

# Snapshot of every key already present in the real process environment at
# this point - i.e. provided by docker's `env_file`/`environment:`, or a real
# `.env` just picked up by load_dotenv() above. The Settings dialog (see
# routers/settings.py, support/runtime_settings.py) treats these as
# read-only: a value someone edits in the UI is only ever allowed to fill in
# a key nobody has actually configured, never override one that has.
ENV_LOCKED_KEYS = frozenset(os.environ.keys())

# Fill in anything previously saved from the Settings dialog - for any key
# not already covered by ENV_LOCKED_KEYS above - so it's visible to the
# os.getenv(...) calls below exactly as if it were a real env var.
from .runtime_settings import apply_stored_overrides  # noqa: E402

apply_stored_overrides(ENV_LOCKED_KEYS)

# Access the variables using os.getenv
trial = False
dev = False
frontmatter_installation = True
if os.getenv("TRIAL") == "True":
    trial = True
    log.info("Running in trial mode")
if os.getenv("DEV") == "True":
    dev = True
    log.info("Running in dev mode")
if os.getenv("FRONTMATTER_INSTALLATION") == "False":
    frontmatter_installation = False
max_nodes = int(os.getenv("MAX_NODES", default="50000"))
cluster_url = os.getenv("CLUSTER_URL", default="")
cluster_user = os.getenv("CLUSTER_USER", default="")
cluster_password = os.getenv("CLUSTER_PASSWORD", default="")
cluster_job_path = os.getenv("CLUSTER_JOB_PATH", default="./PeridigmJobs/apiModels/")  # "./PeridigmJobs/apiModels/"
cluster_perilab_path = os.getenv("CLUSTER_PERILAB_PATH", default="/PeriLab/")  # "./PeridigmJobs/apiModels/"
cluster_enabled = False
if cluster_url != "":
    cluster_enabled = True
    log.info(f"Cluster with url {cluster_url} is enabled")

# --- API-key auth ------------------------------------------------------------
# Comma-separated "name:key" pairs, e.g. "ci:abc123,partner-x:def456".
# Meant for programmatic/CI callers that shouldn't have to go through the
# browser-oriented Keycloak login flow. See support/api_key_auth.py.
api_keys_raw = os.getenv("API_KEYS", default="")

# --- Audit logging -------------------------------------------------------
audit_log_path = os.getenv("AUDIT_LOG_PATH", default=os.path.join(os.path.dirname(__file__), "..", "logs", "audit.log"))

# --- Usage metering -------------------------------------------------------
usage_log_path = os.getenv(
    "USAGE_LOG_PATH", default=os.path.join(os.path.dirname(__file__), "..", "logs", "usage.jsonl")
)

# --- Log-stream websocket ----------------------------------------------------
# How long the /ws log-tail endpoint waits for a job's .log file to show up
# before giving up and reporting an error to the client, instead of failing
# immediately if the job hasn't written anything yet (containers/clusters can
# take a while to actually start the solver process).
ws_log_wait_timeout_seconds = int(os.getenv("WS_LOG_WAIT_TIMEOUT_SECONDS", default="300"))

# --- Job back-pressure -----------------------------------------------------
# Simple in-process concurrency cap on locally-submitted jobs. This is a
# stop-gap, not a replacement for a real distributed queue (Celery/RQ) with
# retries, multi-worker fan-out, and persistence across restarts - see the
# roadmap for that larger follow-up.
max_concurrent_local_jobs = int(os.getenv("MAX_CONCURRENT_LOCAL_JOBS", default="4"))

# --- Solver backend selection ------------------------------
# "local" talks to the bundled perihub_perilab docker container over SSH
# (current/only supported behaviour). "external" is the hook for the planned
# paid feature of pointing at a customer-hosted PeriLab server; it is not
# functionally complete yet - see support/solver_backend.py.
solver_backend_kind = os.getenv("SOLVER_BACKEND", default="local")
external_perilab_url = os.getenv("EXTERNAL_PERILAB_URL", default="")

# --- License server integration ---------------------------------------------
# Assumes a license server already exists and is reachable at
# LICENSE_SERVER_URL; see support/license_client.py for the (documented,
# assumed) request/response contract PeriHub expects from it, and
# support/entitlements.py for how routers gate paid features behind it.
license_server_url = os.getenv("LICENSE_SERVER_URL", default="")
license_key = os.getenv("LICENSE_KEY", default="")
# Unique id for *this* PeriHub instance/install, sent to the license server so
# it can track seat/instance usage independently of any one user account.
license_instance_id = os.getenv("LICENSE_INSTANCE_ID", default="")
license_cache_path = os.getenv(
    "LICENSE_CACHE_PATH", default=os.path.join(os.path.dirname(__file__), "..", "logs", "license_cache.json")
)
# How long a successfully-fetched entitlement grant stays valid before this
# instance tries to refresh it from the license server.
license_refresh_interval_seconds = int(os.getenv("LICENSE_REFRESH_INTERVAL_SECONDS", default=str(60 * 60)))
# If the license server is unreachable, how long PeriHub keeps honouring the
# last-known-good entitlements before falling back to open-core only. Keeps a
# transient outage on the license server from taking down paying customers'
# already-granted features.
license_offline_grace_period_seconds = int(os.getenv("LICENSE_OFFLINE_GRACE_PERIOD_SECONDS", default=str(72 * 60 * 60)))
