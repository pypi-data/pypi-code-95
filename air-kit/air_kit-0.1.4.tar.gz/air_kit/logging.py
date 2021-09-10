from contextvars import ContextVar
from datetime import datetime
from json import dumps
from logging import DEBUG, INFO, Filter, Formatter
from logging.config import dictConfig
from sys import stdout

correlation_id = ContextVar("correlation_id", default="")


def get_correlation_id():
    global correlation_id
    return correlation_id.get()


def set_correlation_id(correlation_id_new):
    global correlation_id
    correlation_id.set(correlation_id_new)


class CustomFilter(Filter):
    def filter(self, record):
        return True


class BaseFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        created = datetime.utcfromtimestamp(record.created)
        return created.isoformat()


class JsonFormatter(BaseFormatter):
    def __init__(self, _, *args, **kwargs):
        super().__init__(
            dumps(
                {
                    "correlation_id": "%(correlation_id)s",
                    "time": "%(asctime)s",
                    "level": "%(levelname)s",
                    "path": "%(pathname)s",
                    "line": "%(lineno)s",
                    "message": "%(message)s",
                }
            ),
            *args,
            **kwargs,
        )

    def format(self, record):
        record.correlation_id = get_correlation_id()
        return super().format(record)


class TextFormatter(BaseFormatter):
    def __init__(self, _, *args, **kwargs):
        super().__init__(
            "%(correlation_id)s %(asctime)s %(levelname)s %(pathname)s %(line)s %(message)s",
            *args,
            **kwargs,
        )

    def format(self, record):
        record.correlation_id = get_correlation_id()
        return super().format(record)


def configure_loggers(
    stream: object,
    formatter: str = "json",
):
    dictConfig(
        {
            "version": 1,
            "filters": {
                "custom": {
                    "()": "air_kit.logging.CustomFilter",
                },
            },
            "formatters": {
                "json": {
                    "class": "air_kit.logging.JsonFormatter",
                },
                "text": {
                    "class": "air_kit.logging.TextFormatter",
                },
            },
            "handlers": {
                "output": {
                    "class": "logging.StreamHandler",
                    "level": DEBUG,
                    "filters": ("custom",),
                    "formatter": formatter,
                    "stream": stream,
                },
            },
            "loggers": {
                "": {
                    "level": DEBUG,
                    "filters": ("custom",),
                    "handlers": ("output",),
                    "propagate": True,
                },
                "urllib3.connectionpool": {
                    "level": INFO,
                    "filters": ("custom",),
                    "handlers": ("output",),
                    "propagate": True,
                },
                "docker.utils.config": {
                    "level": INFO,
                    "filters": ("custom",),
                    "handlers": ("output",),
                    "propagate": True,
                },
                "asyncpgsa.query": {
                    "level": INFO,
                    "filters": ("custom",),
                    "handlers": ("output",),
                    "propagate": True,
                },
            },
        }
    )
