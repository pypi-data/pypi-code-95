# -*- coding: utf-8 -*-
from outflow.ray.task_manager import RayTaskManager


def run_main_workflow(task_list):

    task_manager = RayTaskManager()

    for task in task_list:
        task_manager.compute(task.workflow)

    return [task_manager.results.resolve(task.id) for task in task_list]
