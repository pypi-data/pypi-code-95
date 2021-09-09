from typing import Any, List, Optional, Dict
import json

from pydantic import BaseModel, ValidationError
from dapr.clients import DaprClient
from loguru import logger


class LogEntry(BaseModel):
    uuid: str
    timestamp: int
    level: str
    message: Dict[str, Any]


class Logger:
    """
    Custom logger wrapper to help track and accumulate logs
    Also helps to add types to existing logger
    """

    logs: List[LogEntry]
    uuid: Optional[str]
    handler_id: Optional[int]

    def __init__(self, log: Any = logger):
        self.primary = log
        self.logger = self.primary
        self.logs = []
        self.handler_id = None
        self.uuid = None

    def consume_logs(self) -> List[LogEntry]:
        logs = self.logs
        self.logs = []
        if self.handler_id is not None:
            self.logger.remove(self.handler_id)
        self.logger = self.primary
        self.uuid = None
        self.handler_id = None
        return logs

    def track_message(self, message):

        record = json.loads(message)["record"]
        cleaned = json.loads(message)["record"]
        # Cleanup
        del cleaned["elapsed"]
        del cleaned["thread"]
        del cleaned["process"]
        del cleaned["level"]
        del cleaned["time"]
        self.logs.append(
            LogEntry(
                uuid=self.uuid,
                timestamp=record["time"]["timestamp"],
                level=record["level"]["name"]
                if record["exception"] is None
                else "EXCEPTION",
                message=cleaned,
            )
        )

    def track(self, uuid: str) -> None:
        self.uuid = uuid
        self.logger = self.primary.bind(uuid=uuid)
        self.handler_id = self.logger.add(self.track_message, serialize=True)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.info(msg, *args, **kwargs)

    def success(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.success(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, e: Exception, *args: Any, **kwargs: Any) -> None:
        self.logger.exception(e, *args, **kwargs)
