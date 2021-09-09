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
        # self.logger = self.primary
        self.logs = []
        self.handler_id = None
        self.uuid = None
        self.update_logger(self.primary)

    # We can't have wrapers, otherwise function context gets removed
    def update_logger(self, logger):
        self.logger = logger
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.success = self.logger.success
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception

    def consume_logs(self) -> List[LogEntry]:
        logs = self.logs
        self.logs = []
        if self.handler_id is not None:
            self.logger.remove(self.handler_id)
        self.update_logger(self.primary)
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
        self.update_logger(self.primary.bind(uuid=uuid))
        self.handler_id = self.logger.add(self.track_message, serialize=True)
