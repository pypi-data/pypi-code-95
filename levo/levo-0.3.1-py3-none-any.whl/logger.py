import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import structlog

from .env_constants import LOG_BASE_PATH, LOG_DEFAULT_NAME, LOG_HANDLER, LOG_LEVEL


def get_default_logging_level():
    if LOG_LEVEL == "INFO":
        return logging.INFO
    else:
        return logging.DEBUG


def get_logging_handler():
    if LOG_HANDLER == "FILE":
        handler = RotatingFileHandler(
            os.path.join(LOG_BASE_PATH, LOG_DEFAULT_NAME),
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=10,
            encoding=None,
            delay=0,
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
    return handler


logging.basicConfig(level=get_default_logging_level())
logging.root.handlers = [get_logging_handler()]

timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")


def configure_logging():
    """To be called once during the initialization of the CLI. Sets the global default configuration
    for logging in the CLI. Individual loggers could override some stuff though.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        cache_logger_on_first_use=True,
    )


def get_logger(name=None, level=logging.INFO):
    """Method to be called by the individual modules to get logger. Individual loggers can customize different
    things like the file they log to, etc but the overall format, structure should be driven from the global config.
    """
    log = logging.getLogger(name)
    log.setLevel(level)
    return structlog.wrap_logger(log)


def set_log_level(level):
    logging.root.setLevel(level)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(level)
    for handler in logging.root.handlers:
        handler.setLevel(level)
