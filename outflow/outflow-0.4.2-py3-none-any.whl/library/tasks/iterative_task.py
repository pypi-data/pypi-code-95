# -*- coding: utf-8 -*-
from copy import deepcopy

from outflow.core.tasks import TaskManager
from outflow.core.tasks import Task
from outflow.core.workflow import ManagerTask


class IterativeTask(Task, ManagerTask):
    def __init__(
        self, max_iterations, break_func, name=None, criterion_name="iter_criterion"
    ):
        ManagerTask.__init__(self)

        Task.__init__(self, auto_outputs=False)

        if name is not None:
            self.name = name

        self.criterion_name = criterion_name
        self.break_func = break_func
        self.max_iterations = max_iterations

    def run(self, **inputs):

        inputs_copy = inputs.copy()
        temp_result_dict = {self.criterion_name: None}

        self.setup_external_edges(self.inner_workflow, self.external_edges, inputs_copy)

        for i in range(self.max_iterations):

            workflow_copy = deepcopy(self.inner_workflow)
            workflow_copy.start_nodes()[0].bind(
                **{self.criterion_name: temp_result_dict[self.criterion_name]},
                **inputs_copy
            )

            # execute subworkflow
            task_manager = TaskManager()
            task_manager.compute(workflow_copy)

            terminating_tasks = list()

            # get outputs of last tasks of workflow
            for task in workflow_copy:
                if task.terminating:
                    terminating_tasks.append(task_manager.results[task.id])

            temp_result_dict = terminating_tasks[0]
            if self.break_func(
                **{self.criterion_name: temp_result_dict[self.criterion_name]}
            ):
                break

        return temp_result_dict

    def __exit__(self, *args):

        # move to ManagerTask exit

        start_nodes = self.inner_workflow.start_nodes()
        if len(start_nodes) > 1:
            raise NotImplementedError(
                "Multiple start tasks in iterative workflow not yet supported"
            )
        self.start = start_nodes[0]

        end_nodes = self.inner_workflow.end_nodes()
        if len(end_nodes) > 1:
            raise NotImplementedError(
                "Multiple end tasks in iterative workflow not yet supported"
            )
        self.end = end_nodes[0]
        self.end.terminating = True

        self.inputs = self.start.inputs.copy()
        self.outputs = self.end.outputs.copy()

        ManagerTask.__exit__(self, *args)

    def check_inputs(self, task_inputs):
        pass
