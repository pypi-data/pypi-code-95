from typing import Any, Dict
import json, traceback, sys

from pydantic import BaseModel, ValidationError
from dapr.clients import DaprClient

from .utils import safe_dump, now, path
from .types import ChildAction, Environment, Task, TaskOutput, PluginOutput
from .logger import Logger


class Worker:
    logger: Logger

    def __init__(self, logger: Logger):
        if not isinstance(logger, Logger):
            raise Exception("Expected a valid nanowire logger")
        self.logger = logger

    def execute(self, task: Any) -> PluginOutput:
        raise Exception("Please define execute method")


class ServiceClient:
    env: Environment
    route: str
    failed: str
    finished: str
    logger: Logger
    worker: Worker

    def __init__(self, env: Any, logger: Logger, worker: Worker):
        self.client = DaprClient()
        self.raw_env = env
        self.env = Environment(**env)
        self.worker = worker

        self.route = "/receive"
        self.logger = logger
        self.failed = "failed"
        self.finished = "finished"
        self.logs = "logs"

    def subscriptions(self):
        return [
            {
                "topic": self.env.DAPR_APP_ID,
                "route": self.route,
                "pubsubname": self.env.PUB_SUB,
            }
        ]

    def handle_request(self, body):
        uuid = path(["uuid"], body)
        if uuid is None:
            raise Exception("No uuid found")

        self.logger.track(uuid)
        self.logger.debug(f"[{uuid}] Task received")
        started = now()
        try:
            task = Task(**body)
            # TODO: if body is an url, should try and retrieve it
            # before passing down for validation
            plugin_result = self.worker.execute(body)
            if not isinstance(plugin_result, PluginOutput):
                raise Exception(
                    "Received invalid task output. Expected PluginOutput, received: {}".format(
                        repr(plugin_result)
                    )
                )
            finished = now()
            self.logger.debug(
                "[{uuid}] Task finished, publishing", uuid=task.uuid
            )
            result = TaskOutput(
                uuid=task.uuid,
                started=started,
                finished=finished,
                output=plugin_result.output,
                actions=plugin_result.actions,
                plugin_id=task.current.id,
            )
            output = result.dict()
            self.publish(self.finished, output)
            self.logger.debug("[{uuid}] Published, done", uuid=task.uuid)
        except ValidationError as e:
            exc_info = sys.exc_info()
            exception = "".join(traceback.format_exception(*exc_info))
            self.logger.error(f"[{uuid}] Failed to parse task body {exception}")
            output = {
                "uuid": uuid,
                "started": started,
                "finished": now(),
                "error": {
                    "body": body,
                    "why": "ValidationError",
                    "errors": json.loads(e.json()),
                },
            }
            self.publish(self.failed, output)
        except Exception as e:
            exc_info = sys.exc_info()
            exception = "".join(traceback.format_exception(*exc_info))
            self.logger.error(f"[{uuid}] Failed to parse task body {exception}")
            output = {
                "uuid": uuid,
                "started": started,
                "finished": now(),
                "error": {
                    "body": body,
                    "why": "Exception",
                    "message": str(e),
                    "type": repr(e),
                    "exception": exception,
                },
            }
            self.publish(self.failed, output)
        logs = self.logger.consume_logs()
        self.publish(self.logs, [log.dict() for log in logs])
        return output

    def publish(self, topic: str, data: Any) -> None:
        self.client.publish_event(
            pubsub_name=self.env.OUTPUT_PUB_SUB,
            topic_name=topic,
            data_content_type="application/json",
            data=safe_dump(data),
        )
