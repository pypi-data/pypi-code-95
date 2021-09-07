import time
from typing import Dict, Any

from atlas_engine_client.core.api import UserTaskQuery

from robot.api import logger

from ._retry_helper import retry_on_exception


class UserTaskKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

        self._max_retries = kwargs.get('max_retries', 5)
        self._backoff_factor = kwargs.get('backoff_factor', 2)
        self._delay = kwargs.get('delay', 0.1)

    @retry_on_exception
    def get_user_task_by(self, **kwargs):

        logger.debug(kwargs)

        query = UserTaskQuery(**kwargs)

        logger.info(query)

        current_retry = 0
        current_delay = self._delay

        while True:
            user_tasks = self._client.user_task_get(query)

            logger.info(user_tasks)

            if len(user_tasks) >= 1:
                user_task = user_tasks[0]
            else:
                user_task = {}

            if user_task:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * self._backoff_factor
                if current_retry > self._max_retries:
                    break
                logger.info(
                    f"Retry count: {current_retry}; delay: {current_delay}")

        return user_task

    @retry_on_exception
    def finish_user_task(self, user_task_instance_id: str, payload: Dict[str, Any]):
        self._client.user_task_finish(user_task_instance_id, payload)
