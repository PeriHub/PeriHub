# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(level=logging.INFO)],
)
logging.getLogger("matplotlib").setLevel(logging.ERROR)
logging.getLogger("paramiko").setLevel(logging.WARNING)

log = logging.getLogger("rich")

dev = [False]

dlr = [False]