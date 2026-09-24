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

# --- Multi-user database (Phase 0) -------------------------------------------
# Postgres connection for accounts, org settings, and (Phase 1) shared model
# configs/materials. e.g. postgresql+psycopg://user:pass@host:5432/perihub
# Left empty, trial mode still works (ephemeral, no DB); community/enterprise
# deployments should always set this. See db/base.py.
database_url = os.getenv("DATABASE_URL", default="")

# Signing secret for local-auth session JWTs (support/local_auth.py). Must be
# set to a long random value for local email/password login to work - there
# is deliberately no insecure default here.
session_secret = os.getenv("SESSION_SECRET", default="")
session_ttl_seconds = int(os.getenv("SESSION_TTL_SECONDS", default=str(60 * 60 * 24 * 7)))  # 7 days

# --- Deployment mode -----------------------------------------------------
# "trial" | "community" | "enterprise". Distinct from license_server_url:
# trial has no persistent accounts at all (random per-session identity, see
# db_auth.py), which isn't something a license grant toggles on its own.
# community/enterprise both persist accounts; enterprise additionally
# requires a valid license (see support/entitlements.py) to unlock
# OAuth2/OIDC login and seat enforcement.
deployment_mode = os.getenv("DEPLOYMENT_MODE", default="trial" if trial else "community")

# --- API-key auth ------------------------------------------------------------
# Comma-separated "name:key" pairs, e.g. "ci:abc123,partner-x:def456".
# Meant for programmatic/CI callers that shouldn't have to go through the
# browser-oriented OAuth/OIDC login flow. See support/api_key_auth.py.
api_keys_raw = os.getenv("API_KEYS", default="")

# --- Audit logging -------------------------------------------------------
audit_log_path = os.getenv(
    "AUDIT_LOG_PATH",
    default=os.path.join(os.path.dirname(__file__), "..", "logs", "audit.log"),
)

# --- Usage metering -------------------------------------------------------
usage_log_path = os.getenv(
    "USAGE_LOG_PATH",
    default=os.path.join(os.path.dirname(__file__), "..", "logs", "usage.jsonl"),
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

# --- Compute fairness (Phase 3) ------------------------------------------
# Per-user cap on simultaneously queued+running local jobs - stops one user
# from filling the whole instance-wide slot pool above even when they're
# well under max_concurrent_local_jobs. Requires DATABASE_URL (queue state
# lives in job_queue_entries); without a DB, only the flat instance-wide
# cap above applies (support/job_concurrency.py falls back automatically).
max_concurrent_jobs_per_user = int(os.getenv("MAX_CONCURRENT_JOBS_PER_USER", default="2"))

# How often the background scheduler (support/job_queue.py, started from
# main.py's lifespan) checks for free capacity and dequeues the next job.
job_scheduler_interval_seconds = float(os.getenv("JOB_SCHEDULER_INTERVAL_SECONDS", default="5"))

# Node-count thresholds for the pre-submit cost estimate (support/job_cost.py).
# Purely advisory - never blocks a submission, just returns a warning string
# the frontend can show the user before they confirm.
job_cost_warn_node_count = int(os.getenv("JOB_COST_WARN_NODE_COUNT", default="100000"))
job_cost_block_confirm_node_count = int(os.getenv("JOB_COST_CONFIRM_NODE_COUNT", default="500000"))

# --- Solver backend selection ------------------------------
# Both "local" and "external" now talk to a PeriLab API server (see
# support/perilab_api_client.py) instead of running PeriLab directly -
# "local" is the bundled perihub_perilab container (reachable over the
# docker-compose network at local_perilab_api_url, and sharing the
# `perihub` volume with this container, so job files don't need to be
# uploaded/downloaded - see support/solver_backend.py), "external" is a
# customer-hosted PeriLab API instance reachable only over HTTP, so files
# are uploaded/downloaded through the API instead.
solver_backend_kind = os.getenv("SOLVER_BACKEND", default="local")
local_perilab_api_url = os.getenv("LOCAL_PERILAB_API_URL", default="http://localhost:3000")
external_perilab_url = os.getenv("EXTERNAL_PERILAB_URL", default="")
# How long to wait on a single call to the PeriLab API before giving up.
perilab_api_timeout_seconds = float(os.getenv("PERILAB_API_TIMEOUT_SECONDS", default="30"))

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
    "LICENSE_CACHE_PATH",
    default=os.path.join(os.path.dirname(__file__), "..", "logs", "license_cache.json"),
)
# How long a successfully-fetched entitlement grant stays valid before this
# instance tries to refresh it from the license server.
license_refresh_interval_seconds = int(os.getenv("LICENSE_REFRESH_INTERVAL_SECONDS", default=str(60 * 60)))
# If the license server is unreachable, how long PeriHub keeps honouring the
# last-known-good entitlements before falling back to open-core only. Keeps a
# transient outage on the license server from taking down paying customers'
# already-granted features.
license_offline_grace_period_seconds = int(os.getenv("LICENSE_OFFLINE_GRACE_PERIOD_SECONDS", default=str(72 * 60 * 60)))

# --- OAuth2/OIDC login (Phase 1, enterprise-only) ----------------------------
# Gated by support/entitlements.require_feature("oauth_login") - only
# reachable at all with a license that grants it. Standard authorization-code
# flow against any IdP that publishes a discovery document at
# OAUTH_DISCOVERY_URL (".../.well-known/openid-configuration"); PeriHub
# performs the code exchange itself using these values (see
# support/oidc_client.py). This also covers a self-hosted Keycloak realm -
# point OAUTH_DISCOVERY_URL at
# "{your-keycloak-url}/realms/{your-realm}/.well-known/openid-configuration"
# and set OAUTH_CLIENT_ID/OAUTH_CLIENT_SECRET to that realm's client
# credentials; there's no separate Keycloak-specific login path any more.
oauth_discovery_url = os.getenv("OAUTH_DISCOVERY_URL", default="")  # e.g. https://idp/.well-known/openid-configuration
oauth_client_id = os.getenv("OAUTH_CLIENT_ID", default="")
oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET", default="")
oauth_redirect_uri = os.getenv("OAUTH_REDIRECT_URI", default="")
