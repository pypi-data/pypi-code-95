# -*- coding: utf-8 -*-
from outflow.core.results import Results
from outflow.core.target import TargetException
from outflow.core.types import Skipped


class TaskManager:
    """
    Manage task calls and store the result references
    """

    def __init__(self):
        # to avoid reprocessing, store a reference of each task result for each already visited graph node
        self.results = Results()

    def compute(self, workflow):

        from outflow.library.tasks import MergeTask

        # run through each task of the workflow to gather task result references
        for task in workflow.sorted_tasks():
            if task.id in self.results:
                # avoid reprocessing already visited graph nodes
                continue

                # create a dictionary to store the reference to the task inputs
            task_inputs = {}

            # loop over the task parents to get the task inputs
            for parent in task.parents:
                # ensure the parents result reference is already stored in the promises reference dict

                # and loop over parents
                if isinstance(task, MergeTask):
                    for output_key in parent.outputs:
                        task_inputs[
                            parent.name + "_" + output_key
                        ] = self.results.get_item_reference(parent.id, output_key)
                else:
                    for output_key in parent.outputs:
                        task_inputs[output_key] = self.results.get_item_reference(
                            parent.id, output_key
                        )

            task_return_value = self.run(task, task_inputs)
            task_return_value = self.post_process(task, task_return_value)

            self.results._set(task.id, task_return_value)

    def run(self, task, task_inputs):
        return task(**task_inputs)

    def post_process(self, task, task_return_value):
        post_processed = task_return_value

        if not isinstance(task_return_value, dict):
            if isinstance(task_return_value, Skipped):
                # if the returned object is Skipped(), put skipped in all outputs
                post_processed = {output: task_return_value for output in task.outputs}
            elif len(task.outputs) > 1:
                raise TargetException(
                    f"Task {task.name} must return a dictionary since it has defined more than one output target"
                )
            elif len(task.outputs) == 1:
                # If an object is returned and task defined only 1 output
                # -> put the object in a dictionary with the output name as the key
                post_processed = {
                    next(iter(task.outputs)): task_return_value
                }  # get first and only item in dictionary task.outputs

        return post_processed
