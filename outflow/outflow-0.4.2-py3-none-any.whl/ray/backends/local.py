# -*- coding: utf-8 -*-
import ray

from outflow.core.pipeline import context, config
from outflow.ray.task_manager import RayTaskManager


class LocalRayBackend:
    def __init__(self):
        super().__init__()
        ray_params = {}
        num_cpus = config["ray"].get("num_cpus", False)
        if num_cpus:
            ray_params["num_cpus"] = num_cpus
        ray_info = ray.init(log_to_driver=False, **ray_params)
        context.redis_address = ray_info["redis_address"].split(":")[0]

    def run(self, task_list):
        task_manager = RayTaskManager()

        for task in task_list:
            task_manager.compute(task.workflow)

        return [task_manager.results.resolve(task.id) for task in task_list]

    def clean(self):
        pass
