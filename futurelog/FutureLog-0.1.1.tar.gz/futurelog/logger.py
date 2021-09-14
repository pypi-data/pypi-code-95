"""Defer logs to consume them when wanted.

Main usecase for this library is when we want to show logs by block in an async environment,
such as deployers reports.
"""
import logging
import logging.config
import os
import time
from collections import defaultdict, namedtuple
from typing import Dict, List

DEFAULT_LOG_LEVEL = logging.getLevelName(os.getenv("LOG_LEVEL", "INFO").upper())

FutureLog = namedtuple("FutureLog", "time logger level msg args")


class FutureLogger:
    """Defer logs until we explicitly want to 'show' them."""

    ALL_LOGGERS: List = []

    def __init__(self, name: str, log_level: int = DEFAULT_LOG_LEVEL) -> None:
        """Initialize a FutureLogger collector."""
        self.name = name
        self.logs: Dict[str, List] = defaultdict(list)

        self.logger = logging.getLogger(name.split(".").pop())
        self.logger.setLevel(log_level)

        # register instance
        self.ALL_LOGGERS.append(self)

    def _record_log(self, identifier: str, msg: str, level: int, *args: str) -> None:
        log = FutureLog(time.time(), self.logger, level, msg, args)
        self.logs[identifier].append(log)

    def consume(self, identifier: str) -> None:
        """Pop and print log for one identifier."""
        if identifier not in self.logs:
            return

        logs = self.logs.pop(identifier)
        for log in logs:
            self.logger.log(log.level, log.msg, *log.args)

    def consume_all(self) -> None:
        """Pop and print log for one identifier."""
        for all_logs in self.logs.values():
            for log in all_logs:
                self.logger.log(log.level, log.msg, *log.args)

        self.logs = defaultdict(list)

    @classmethod
    def consume_all_logger(cls):
        """Consume all logs from all loggers."""
        all_logs = []

        # we get all logs from all logger
        for logger in cls.ALL_LOGGERS:
            for logs in logger.logs.values():
                all_logs.extend(logs)
                logger.logs = defaultdict(list)

        # we sort the logs and then we consume them
        sorted_logs = sorted(all_logs, key=lambda x: x.time)
        for log in sorted_logs:
            log.logger.log(log.level, log.msg, *log.args)

    @classmethod
    def consume_all_logger_for(cls, identifier: str) -> None:
        """Consume all logs from all loggers for one identifier."""
        all_logs = []

        # we get all logs from all logger
        for logger in cls.ALL_LOGGERS:
            if identifier not in logger.logs:
                continue
            logs = logger.logs.pop(identifier)
            all_logs.extend(logs)

        # we sort the logs and then we consume them
        sorted_logs = sorted(all_logs, key=lambda x: x.time)
        for log in sorted_logs:
            log.logger.log(log.level, log.msg, *log.args)

    def debug(self, identifier: str, msg: str, *args: str) -> None:
        """Record future 'debug' log."""
        self._record_log(identifier, msg, logging.DEBUG, *args)

    def info(self, identifier: str, msg: str, *args: str) -> None:
        """Record future 'info' log."""
        self._record_log(identifier, msg, logging.INFO, *args)

    def warning(self, identifier: str, msg: str, *args: str) -> None:
        """Record future 'warning' log."""
        self._record_log(identifier, msg, logging.WARNING, *args)

    def error(self, identifier: str, msg: str, *args: str) -> None:
        """Record future 'error' log."""
        self._record_log(identifier, msg, logging.ERROR, *args)

    def critical(self, identifier: str, msg: str, *args: str) -> None:
        """Record future 'critical' log."""
        self._record_log(identifier, msg, logging.CRITICAL, *args)
