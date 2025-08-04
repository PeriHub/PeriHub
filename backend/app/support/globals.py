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
if os.getenv("TRIAL") == "True":
    trial = True
    log.info("Running in trial mode")
if os.getenv("DEV") == "True":
    dev = True
    log.info("Running in dev mode")
max_nodes = int(os.getenv("MAX_NODES", default="10000"))
cluster_url = os.getenv("CLUSTER_URL", default="")
cluster_user = os.getenv("CLUSTER_USER", default="")
cluster_password = os.getenv("CLUSTER_PASSWORD", default="")
cluster_job_path = os.getenv("CLUSTER_JOB_PATH", default="./PeridigmJobs/apiModels/")  # "./PeridigmJobs/apiModels/"
cluster_perilab_path = os.getenv("CLUSTER_PERILAB_PATH", default="/PeriLab/")  # "./PeridigmJobs/apiModels/"
cluster_enabled = False
if cluster_url != "":
    cluster_enabled = True
    log.info(f"Cluster with url {cluster_url} is enabled")
