import logging
import datetime
from typing import Any

from solitude import TOOL_NAME


class TimeLogger(object):
    def __enter__(self) -> Any:
        self._start_wall_time = datetime.datetime.now()
        self._stop_wall_time = self._start_wall_time
        return self

    def __exit__(self, typ: Any, value: Any, traceback: Any) -> Any:
        self._stop_wall_time = datetime.datetime.now()
        return self

    def __str__(self) -> str:
        wall_time_elapsed = self._stop_wall_time - self._start_wall_time
        return f"{self._stop_wall_time} (runtime: {wall_time_elapsed})"


class ActionTimeLogger(TimeLogger):
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(TOOL_NAME)

    def __enter__(self) -> Any:
        super().__enter__()
        self._logger.debug(f"Starting action at: {self._start_wall_time}")
        return self

    def __exit__(self, typ: Any, value: Any, traceback: Any) -> Any:
        super().__exit__(typ, value, traceback)
        self._logger.debug(str(self))
        return self

    def __str__(self) -> str:
        return f"Finished action at: {super().__str__()}"
