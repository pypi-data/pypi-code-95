# -*- coding: utf-8 -*-
import ray
from outflow.core.tasks import TaskManager


@ray.remote
class IterativeLoopActor:
    def __init__(
        self,
        entrypoint,
        max_iterations,
        # break_on,
        # break_at,
        post_process,
        outputs,
    ):
        self.entrypoint = entrypoint
        self.max_iterations = max_iterations
        # self.break_on = break_on
        # self.break_at = break_at
        self.post_process = post_process
        self.outputs = outputs

    def run(self, **loop_inputs):
        temp_result = 1  # change to none and handle in first task of the loop or in loop class maybe

        loop_workflow = self.entrypoint.workflow
        loop_workflow.entrypoint = self.entrypoint

        for i in range(self.max_iterations):
            workflow_copy = loop_workflow.copy()
            workflow_copy.entrypoint.bind(
                **{"prev_result": temp_result, "iteration": i}
            )
            task_manager = TaskManager()
            task_manager.compute(workflow_copy)
            lazy_result = [
                loop_inputs[task.id] for task in workflow_copy if task.terminating
            ]
            temp_result = ray.get(lazy_result[0])
            if self.break_func(**temp_result):
                temp_result = int(temp_result[self.outputs[0]])
                break

            temp_result = int(temp_result[self.outputs[0]])

        return self.post_process(temp_result)

    def break_func(self, **loop_inputs):
        if loop_inputs.get("output2", 0) >= 10:  # TODO change this
            return True
        else:
            return False

    # def post_process(self, **kwargs):
    #     return {'iter_loop_result': x}  # FIXME
