import logging
import json
import time

from collections import OrderedDict

from .json_encoder import _JsonEncoder


class GCloudFormatter(logging.Formatter):
    def __init__(self, prefix: str = "", **kwargs):
        self._prefix = prefix
        super().__init__(**kwargs)

    LOG_ENTRY_RESERVED_ATTRIBUTES = (
        'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelname', 'levelno', 'lineno', 'module',
        'msecs', 'msg', 'name', 'pathname', 'processName', 'relativeCreated', 'stack_info', 'threadName'
    )

    def format(self, record):
        """Formats a log record and serializes to json"""

        # see https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
        log_record = OrderedDict({
            'message': self._prefix + record.getMessage(),
            'timestamp': self._format_timestamp(record.created),
            'severity': record.levelname,
            'logName': record.module,
        })

        for attr, value in record.__dict__.items():
            if not attr.startswith('__') and attr not in self.LOG_ENTRY_RESERVED_ATTRIBUTES:
                log_record[attr] = value

        if record.exc_info and 'exc_info' not in log_record:
            log_record.exc_info = self.formatException(record.exc_info)

        if record.stack_info and 'stack_info' not in log_record:
            log_record.stack_info = self.formatStack(record.stack_info)

        return json.dumps(log_record, cls=_JsonEncoder)

    @staticmethod
    def _format_timestamp(timestamp: float):
        return time.strftime(f'%Y-%m-%dT%H:%M:%S.{repr(timestamp).split(".")[1]}00Z', time.gmtime(timestamp))
