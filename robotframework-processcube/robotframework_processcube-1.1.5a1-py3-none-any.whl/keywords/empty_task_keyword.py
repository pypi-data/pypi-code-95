import time

from atlas_engine_client.core.api import EmptyTaskQuery

from robot.api import logger

from ._retry_helper import retry_on_exception


class EmptyTaskKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

        self._max_retries = kwargs.get('max_retries', 5)
        self._backoff_factor = kwargs.get('backoff_factor', 2)
        self._delay = kwargs.get('delay', 0.1)

    @retry_on_exception
    def get_empty_task_by(self, **kwargs):

        logger.debug(kwargs)

        query = EmptyTaskQuery(**kwargs)

        logger.info(query)

        current_retry = 0
        current_delay = self._delay

        while True:
            empty_tasks = self._client.empty_task_get(query)

            logger.info(empty_tasks)

            if len(empty_tasks) >= 1:
                empty_task = empty_tasks[0]
            else:
                empty_task = {}

            if empty_task:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * self._backoff_factor
                if current_retry > self._max_retries:
                    break
                logger.info(
                    f"Retry count: {current_retry}; delay: {current_delay}")

        return empty_task

    @retry_on_exception
    def finish_empty_task(self, empty_task_instance_id: str):
        self._client.empty_task_finish(empty_task_instance_id)
