import logging
from typing import Type, List, Optional

from .src.gcloud_formatter import GCloudFormatter
from .src.base_context_filter import BaseContextFilter


class GCloudLogConfig:
    DEFAULT_HANDLER = "gcloud_logging"

    def __init__(self, *args: Type[BaseContextFilter], prefix: str = "", level: str = logging.DEBUG):
        self._filters = {}
        self.prefix = prefix
        self._level = logging.getLevelName(level)
        self._extra_loggers = {}
        [self._filters.update({arg.filter_name(): arg}) for arg in args if issubclass(arg, BaseContextFilter)]

    def _get_root(self):
        return {
            "handlers": [self.DEFAULT_HANDLER],
            "level": self._level,
            "propagate": True
        }

    def _get_handlers(self):
        return {
            self.DEFAULT_HANDLER: {
                "class": "logging.StreamHandler",
                "formatter": "gcloud",
                "stream": "ext://sys.stdout",
                "level": "DEBUG",
                "filters": []
            }
        }

    def _get_formatters(self):
        return {
            "gcloud": {
                "()": GCloudFormatter,
                "prefix": self.prefix
            }
        }

    def _get_loggers(self):
        base_logger = {
            "handlers": [self.DEFAULT_HANDLER],
            "level": self._level,
            "propagate": True
        }
        loggers = {
            "": base_logger
        }
        [loggers.update({name: extra_logger}) for name, extra_logger in self._extra_loggers.items()]
        return loggers

    def add_logger(self, name, *, filters: Optional[List[Type[BaseContextFilter]]] = None, level: int = logging.DEBUG):
        self._extra_loggers.update({
            name: {
                "handlers": [self.DEFAULT_HANDLER],
                "level": logging.getLevelName(level),
                "filters": filters if filters else self._filters.keys(),
                "propagate": False
            }
        })

    def _get_filters(self):
        return {
            name: {"()": custom_filter} for name, custom_filter in self._filters.items()
        }

    def add_filter(self, klass: Type[BaseContextFilter]):
        if not issubclass(klass, BaseContextFilter):
            raise ValueError("Filter class must implement logging.Filter class")
        self._filters.update({klass.filter_name(): {"()": klass}})

    @property
    def config(self):
        log_config = {
            "version": 1,
            "root": self._get_root(),
            "handlers": self._get_handlers(),
            "filters": self._get_filters(),
            "formatters": self._get_formatters(),
            "loggers": self._get_loggers()
        }

        for name, custom_filter in self._filters.items():
            log_config['handlers'][self.DEFAULT_HANDLER]['filters'].append(name)

        return log_config
