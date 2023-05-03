import logging

import rich.progress
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(level=logging.ERROR)],
)
logging.getLogger("matplotlib").setLevel(logging.ERROR)
logging.getLogger("paramiko").setLevel(logging.WARNING)

log = logging.getLogger("rich")
