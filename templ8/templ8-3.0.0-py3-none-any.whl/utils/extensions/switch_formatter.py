from logging import DEBUG, Formatter, Logger, LogRecord
from typing import Any


class SwitchFormatter(Formatter):
    parent: Logger

    def __init__(self, parent: Logger, *args: Any, **kwargs: Any) -> None:
        self.parent = parent
        super().__init__(*args, **kwargs)

    def format(self, record: LogRecord) -> str:
        prefix = "%(asctime)s %(name)s:\n"
        msg = "%(message)s"
        suffix = "\n"

        # If the logger's level DEBUG then insert a timestamp into
        # all logger calls, even those at higher log levels.
        # pylint: disable = W0212
        self._style._fmt = (
            prefix + msg + suffix if self.parent.getEffectiveLevel() <= DEBUG else msg
        )

        return Formatter.format(self, record)
