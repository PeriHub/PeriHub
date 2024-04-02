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
if os.getenv("DEV") == "True":
    dev = True
cluster_url = os.getenv("CLUSTER_URL", default="")
cluster_user = os.getenv("CLUSTER_USER", default="")
cluster_password = os.getenv("CLUSTER_PASSWORD", default="")
cluster_enabled = False
if cluster_url != "":
    cluster_enabled = True
