import unittest

import logging
import logging.config
import collections


class LoggerTestCase(unittest.TestCase):
    _formatter = None
    logger_name = __name__

    def setUp(self) -> None:
        if not self._formatter:
            raise Exception("_formatter must be defined")
        if not self.logger:
            logger = logging.getLogger()
            self.memory_logger = MemoryLogger()
            log_handler = self.memory_logger.handler
            log_handler.setFormatter(self._formatter())
            logger.addHandler(log_handler)
            logger.setLevel(logging.DEBUG)

            self.logger = logger


class MemoryLoggerHandler(logging.Handler):
    def __init__(self, log_collection):
        super().__init__(logging.DEBUG)
        self._log_records = log_collection

    def emit(self, record: logging.LogRecord) -> None:
        self._log_records.append(self.format(record))


class MemoryLogger:
        def __init__(self):
            self._log_collection = collections.deque(maxlen=5)
            self._handler = MemoryLoggerHandler(self._log_collection)

        @property
        def handler(self):
            return self._handler

        @property
        def last_record(self):
            try:
                return self._log_collection.pop()
            except IndexError as e:
                return None
