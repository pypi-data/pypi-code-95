import logging
from datetime import datetime

import json_log_formatter

from django_json_logging.context import RequestContext


class JSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message: str, extra: dict, record: logging.LogRecord) -> dict:
        extra["time"] = datetime.utcnow()
        extra["level"] = record.levelname
        extra["name"] = record.name
        extra["message"] = message
        extra["exc_info"] = record.exc_info
        extra["exc_text"] = record.exc_text
        extra.update(RequestContext.to_dict())
        return {k: str(v) for k, v in extra.items() if v is not None}
