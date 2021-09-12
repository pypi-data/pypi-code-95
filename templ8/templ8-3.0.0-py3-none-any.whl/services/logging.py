from logging import Logger, getLogger
from subprocess import PIPE, STDOUT, Popen
from typing import List

from ..utils.extensions.progress_handler import ProgressHandler
from ..utils.extensions.switch_formatter import SwitchFormatter

root_logger = getLogger("root")


def init_root_logger(level: int) -> None:
    progress_handler = ProgressHandler(root_logger)
    progress_handler.setFormatter(SwitchFormatter(root_logger))
    root_logger.addHandler(progress_handler)
    root_logger.setLevel(level)


def flush_progress_handler() -> None:
    for handler in root_logger.handlers:
        if isinstance(handler, ProgressHandler):
            handler.overwrite()
            break


def log_process(logger: Logger, cmd: List[str], cwd: str) -> None:
    with Popen(cmd, cwd=cwd, stdout=PIPE, stderr=STDOUT) as proc:
        if proc.stdout is not None:
            for line in iter(proc.stdout.readline, b""):
                logger.info(line.decode("utf8").rstrip(), extra={"progress": True})
