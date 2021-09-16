import os
import time
import json
import datetime
import logging
from logging.handlers import RotatingFileHandler
import pprint

from gaea.config import CONFIG


# class ContextFilter(logging.Filter):
#     def filter(self, record):
#         if flask.has_request_context():
#             # when logging out, the user_id is already set
#             if not hasattr(record, "user_id"):
#                 record.user_id = flask.session.get("user_id") or 0

#             record.request_form = {
#                 key: item
#                 for key, item in flask.request.form.items()
#                 if key not in ("password", "pwd")
#             }

#             record.request_id = flask.g.request_uuid
#             record.request_path = flask.request.path
#             record.request_method = flask.request.method
#             record.request_user_agent = flask.request.user_agent
#             record.request_ip_address = flask.request.remote_addr
#         return True


class CustomLogger(logging.Logger):
    """Custom logger"""

    # pylint: disable=arguments-differ

    def debug(self, msg, *args, exc_info=False, stack_info=False, **kwargs):
        self._log(
            logging.DEBUG,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )

    def info(self, msg, *args, exc_info=False, stack_info=False, **kwargs):
        self._log(
            logging.INFO,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )

    def warning(self, msg, *args, exc_info=False, stack_info=False, **kwargs):
        self._log(
            logging.WARNING,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )

    def critical(self, msg, *args, exc_info=False, stack_info=False, **kwargs):
        self._log(
            logging.CRITICAL,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )

    def error(self, msg, *args, exc_info=False, stack_info=False, **kwargs):
        self._log(
            logging.ERROR,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )

    def exception(self, msg, *args, stack_info=False, exc_info=True, **kwargs):
        self._log(
            logging.ERROR,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra={"extra": kwargs},
        )


EXCLUDED_FIELDS = (
    "msg",
    "asctime",
    "args",
    "filename",
    "module",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "levelno",
)


class BaseFormatter(logging.Formatter):
    converter = time.gmtime

    def formatTime(self, record, datefmt):
        return datetime.datetime.fromtimestamp(
            record.created, tz=datetime.timezone.utc
        ).isoformat()

    def format(self, record):
        record.message = record.getMessage()
        setattr(record, "timestamp", self.formatTime(record, self.datefmt))

        return {
            key: item
            for key, item in record.__dict__.items()
            if item is not None and key not in EXCLUDED_FIELDS
        }


class JSONFormatter(BaseFormatter):
    def format(self, record):
        log_data = super().format(record)
        return json.dumps(log_data, default=str)


class PrettyJSONFormatter(BaseFormatter):
    def format(self, record):
        log_data = super().format(record)
        return pprint.pformat(log_data)


LOG_LEVEL = CONFIG.get("LOG_LEVEL", logging.INFO)
logger = CustomLogger(CONFIG.SERVICE_NAME)
logger.setLevel(LOG_LEVEL)

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

json_formatter = JSONFormatter(datefmt=DATE_FORMAT)
pretty_json_formatter = PrettyJSONFormatter(datefmt=DATE_FORMAT)
normal_formatter = logging.Formatter(
    fmt="{asctime} | {levelname:8s} | {message}",
    datefmt=DATE_FORMAT,
    style="{",
)


if CONFIG.get("LOG_TO_FILE"):
    log_file_name = f"{CONFIG.SERVICE_NAME}.log"
    log_path = os.path.join(CONFIG.LOGS_FOLDER_NAME, log_file_name)
    file_handler = RotatingFileHandler(log_path, "a", 1_000_000, 100)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)


stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOG_LEVEL)

if CONFIG.get("LOG_FORMAT") == "minimize":
    stream_log_format = normal_formatter
else:
    stream_log_format = pretty_json_formatter

stream_handler.setFormatter(stream_log_format)
logger.addHandler(stream_handler)


# add context within flask.request context
# def init_logging_filter():
#     context_filter = ContextFilter()
#     logger.addFilter(context_filter)
