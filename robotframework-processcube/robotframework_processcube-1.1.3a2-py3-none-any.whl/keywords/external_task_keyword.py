
import time
from typing import Dict, Any

from atlas_engine_client.core.api import FetchAndLockRequestPayload
from atlas_engine_client.core.api import FinishExternalTaskRequestPayload

from robot.api import logger

from ._retry_helper import retry_on_exception


class ExternalTaskKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

    @retry_on_exception
    def get_external_task(self, topic: str, options: dict = {}):

        request = FetchAndLockRequestPayload(
            worker_id=self._worker_id,
            topic_name=topic,
            max_tasks=1
        )

        logger.info(f"get task with {request}")

        current_retry = 0
        current_delay = self._delay

        while True:
            external_tasks = self._client.external_task_fetch_and_lock(request)

            logger.info(external_tasks)

            if len(external_tasks) == 1:
                external_task = external_tasks[0]
            else:
                external_task = {}

            if external_task:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * self._backoff_factor
                if current_retry > self._max_retries:
                    break
                logger.info(
                    f"Retry count: {current_retry}; delay: {current_delay}")

        return external_task

    @retry_on_exception
    def finish_external_task(self, external_task_id: str, result: Dict[str, Any]):
        request = FinishExternalTaskRequestPayload(
            worker_id=self._worker_id,
            result=result
        )

        logger.info(f"finish task with {request}")

        self._client.external_task_finish(external_task_id, request)
