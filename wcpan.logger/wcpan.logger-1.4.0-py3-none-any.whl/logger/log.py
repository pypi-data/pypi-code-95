import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Iterable, List, Optional


class Logger(object):

    def __init__(self, name: str, level: str,
                 exception: Optional[Exception]) -> None:
        super().__init__()
        self._logger = logging.getLogger(name)
        self._level = level
        self._parts = []
        self._exception = exception

    def __lshift__(self, part: Any) -> 'Logger':
        self._parts.append(str(part))
        return self

    def __del__(self) -> None:
        msg = ' '.join(self._parts)
        log = getattr(self._logger, self._level)
        log(msg, exc_info=self._exception)


def DEBUG(name: str) -> Logger:
    return Logger(name, 'debug', None)


def INFO(name: str) -> Logger:
    return Logger(name, 'info', None)


def WARNING(name: str) -> Logger:
    return Logger(name, 'warning', None)


def ERROR(name: str) -> Logger:
    return Logger(name, 'error', None)


def CRITICAL(name: str) -> Logger:
    return Logger(name, 'critical', None)


def EXCEPTION(name: str, exception: Exception = None) -> Logger:
    return Logger(name, 'exception', exception)


def setup(log_name_list: Iterable[str],
          file_path: str = None) -> List[logging.Logger]:
    name_list = [name for name in log_name_list]
    max_name_size = max((len(name) for name in name_list))
    formatter = DynamicFormatter(name_size=max_name_size, thread_name_size=10)
    handler = create_handler(file_path, formatter)
    loggers = [create_logger(name, handler) for name in log_name_list]
    return loggers


def create_handler(path: Optional[str],
                   formatter: logging.Formatter) -> logging.Handler:
    if path:
        # rotate on Sunday
        handler = TimedRotatingFileHandler(path, when='w6', atTime=datetime.time())
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def create_logger(name: str, handler: logging.Handler) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


class DynamicFormatter(object):

    FORMAT = (
        '{{asctime}}|'
        '{{threadName:_<{thread_name_size}.{thread_name_size}}}|'
        '{{levelname:_<1.1}}|'
        '{{name:_<{name_size}.{name_size}}}|'
        '{{message}}'
    )

    def __init__(self, name_size: int, thread_name_size: int):
        self._name_size = name_size
        self._thread_name_size = thread_name_size
        self._formatter = self._create_formatter()

    def _create_formatter(self):
        format = self.FORMAT.format(
            name_size=self._name_size,
            thread_name_size=self._thread_name_size,
        )
        return logging.Formatter(format, style='{')

    def format(self, record: logging.LogRecord):
        changed = False
        if len(record.name) > self._name_size:
            self._name_size = max(len(record.name), self._name_size)
            changed = True
        if record.threadName and len(record.threadName) > self._thread_name_size:
            self._thread_name_size = max(len(record.threadName), self._thread_name_size)
            changed = True
        if changed:
            self._formatter = self._create_formatter()
        return self._formatter.format(record)
