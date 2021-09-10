from logging import getLogger
from time import time_ns

logger = getLogger(__name__)


class Profiler:
    def __init__(self, message, arguments=None, *, enabled=True):
        if arguments is None:
            arguments = {}

        self.message = message
        self.arguments = arguments
        self.enabled = enabled
        self.time_start = None

    def __enter__(self):
        if self.enabled:
            self.time_start = time_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enabled:
            self.arguments["time_delta"] = (
                time_ns() - self.time_start
            ) / 1000000000
            logger.info(self.message.format(**self.arguments))

        return exc_type is None
