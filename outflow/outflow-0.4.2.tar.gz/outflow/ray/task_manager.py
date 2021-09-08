# -*- coding: utf-8 -*-
from outflow.core.tasks import TaskManager
from outflow.ray.results import RayResults

from ray._raylet import ObjectRef


class RayTaskManager(TaskManager):
    def __init__(self):
        super().__init__()
        self.results = RayResults()

    def post_process(self, task, task_return_value):
        post_processed = task_return_value
        if task_return_value is not None and not isinstance(
            task_return_value, ObjectRef
        ):
            post_processed = super().post_process(task, task_return_value)

        return post_processed
