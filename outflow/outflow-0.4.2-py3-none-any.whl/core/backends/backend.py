# -*- coding: utf-8 -*-
from outflow.core.tasks.io_checker import IOChecker
from outflow.core.logging import logger
from outflow.core.tasks import TaskManager
from outflow.core.types import Skipped


class Backend:
    def __init__(self):
        logger.debug(f"Initialize backend '{self}'")
        self.name = "default"

    def run(self, *, task_list):

        task_manager = TaskManager()

        for task in task_list:
            task_manager.compute(
                task.workflow
            )  # todo call on top level workflow instead
            # but still return results of task_list, if list is not none

        execution_return = [task_manager.results.resolve(task.id) for task in task_list]
        filter_results = False  # TODO parametrize outside
        if filter_results:
            return list(
                filter(
                    lambda el: not any(isinstance(val, Skipped) for val in el.values()),
                    execution_return,
                )
            )
        else:
            return execution_return

    def check_task_io(self, task_list):
        logger.debug("Checking tasks input and output coherence")
        io_checker = IOChecker()
        for task in task_list:
            io_checker.compute(task.workflow)

    def clean(self):
        pass
