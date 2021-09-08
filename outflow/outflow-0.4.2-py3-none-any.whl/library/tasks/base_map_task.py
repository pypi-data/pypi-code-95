# -*- coding: utf-8 -*-
import traceback
from typing import List

from outflow.core.tasks.io_checker import IOChecker
from outflow.core.logging import logger
from outflow.core.target import Target
from outflow.core.tasks import Task, TaskManager
from outflow.core.types import IterateOn
from outflow.core.workflow import ManagerTask


class BaseMapTask(Task, ManagerTask):
    def __init__(
        self,
        *,
        name=None,
        no_outputs=False,
        output_name="map_output",
        raise_exceptions=False,
    ):
        ManagerTask.__init__(self)
        self.raise_exceptions = raise_exceptions
        if name is not None:
            self.name = name
        self.no_outputs = no_outputs
        self.output_name = output_name
        Task.__init__(self, auto_outputs=False)
        if not self.outputs and not no_outputs:
            self.outputs = {self.output_name: Target(self.output_name, type=List)}

    def __exit__(self, *args):

        start_nodes = self.inner_workflow.start_nodes()
        start_nodes = [
            start for start in start_nodes if start not in self.external_edges
        ]
        if len(start_nodes) > 1:
            raise NotImplementedError(
                "Multiple start tasks in iterative workflow not yet supported"
            )
        self.start = start_nodes[0]

        self.inputs = {
            target.type.__name__[len(IterateOn.prefix) :]
            if target.type.__name__.startswith(IterateOn.prefix)
            else target.name: target
            for target in self.start.inputs.values()
        }

        self.end = self.inner_workflow.end_nodes()[0]
        self.end.terminating = True

        ManagerTask.__exit__(self, *args)

    def run(self, **map_inputs):
        raise NotImplementedError()

    def generator(self, **map_inputs):
        """
        default generator function
        :param map_inputs:
        :return:
        """

        inputs = map_inputs.copy()

        iterable_targets = [
            target
            for target, target in self.start.inputs.items()
            if target.type.__name__.startswith(IterateOn.prefix)
        ]

        if not iterable_targets:
            raise Exception(
                "MapTasks with default generators must have at least one iterated input. (this might change in the future)"
            )

        # sequence_input_names = []
        input_names = []
        sequences = []

        # get IterateOn inputs
        for iterable_target in iterable_targets:
            # get the input name of the sequence to map
            sequence_input_name = iterable_target.type.__name__[len(IterateOn.prefix) :]
            input_names.append(iterable_target.name)
            sequences.append(map_inputs[sequence_input_name])

            del inputs[sequence_input_name]

        for input_values in zip(*sequences):
            vals = {input_names[i]: input_values[i] for i in range(len(input_names))}
            yield {**vals, **inputs}

    def check_inputs(self, task_inputs):
        return None  # TODO fix check_inputs
        not_iterable_inputs = task_inputs.copy()

        iterable_targets = [
            target
            for target, target in self.start.inputs.items()
            if target.type.__name__.startswith(IterateOn.prefix)
        ]

        input_names = []
        sequences = []

        for iterable_target in iterable_targets:

            # get the input name of the sequence to map
            sequence_input_name = iterable_target.type.__name__[len(IterateOn.prefix) :]
            # sequence_input_names.append(sequence_input_name)
            input_names.append(iterable_target.name)
            sequences.append(self.inputs[sequence_input_name])

            del not_iterable_inputs[sequence_input_name]

        vals = {
            **{input_name: None for input_name in input_names},
            **not_iterable_inputs,
        }
        # self.start.bind(**{**vals, **not_iterable_inputs})

        self.run_workflow(
            self.inner_workflow, vals, 0, True, self.external_edges, IOChecker
        )

    @staticmethod
    def run_workflow(
        workflow,
        inputs,
        index,
        raise_exceptions,
        external_edges,
        task_manager=TaskManager,
    ):
        inputs_copy = inputs.copy()
        # bind external dependencies to internal tasks

        ManagerTask.setup_external_edges(workflow, external_edges, inputs_copy)

        workflow.start_nodes()[0].bind(**inputs_copy)
        terminating_tasks = list()

        for task in workflow:
            # task.context = self.pipeline_context
            task.parallel_workflow_id = index

        task_manager = task_manager()

        try:
            task_manager.compute(workflow)

            for task in workflow:
                if task.terminating:
                    terminating_tasks.append(task_manager.results[task.id])

            result = terminating_tasks
        except Exception as e:
            if raise_exceptions:
                raise e
            logger.warning(f"Mapped workflow {index} raised an exception")
            logger.warning(traceback.format_exc())
            result = e

        return result

    def reduce(self, output):
        if self.no_outputs:
            return None
        else:
            return {self.output_name: output}
