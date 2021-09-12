import sys
from logging import DEBUG, Logger, LogRecord, StreamHandler
from typing import Any

import colorama

from ...utils.collections.dicts import key_is_true
from ...utils.strings.formatters import progress


class ProgressHandler(StreamHandler):
    parent: Logger
    overwrite_previous: bool

    def __init__(self, parent: Logger, *args: Any, **kwargs: Any) -> None:
        colorama.init()
        self.parent = parent
        self.overwrite_previous = False
        super().__init__(*args, **kwargs)

    @staticmethod
    def overwrite() -> None:
        sys.stdout.write("\033[F\033[K")
        sys.stdout.flush()

    def emit(self, record: LogRecord) -> None:
        if self.overwrite_previous:
            self.overwrite()

        if (
            key_is_true(record.__dict__, "progress")
            and self.parent.getEffectiveLevel() > DEBUG
        ):
            record.msg = progress(record.msg)
            self.overwrite_previous = True
        else:
            self.overwrite_previous = False

        super().emit(record)
