# -*- coding: utf-8 -*-
from outflow.ray.actors import IterativeLoopActor

from .task import Task


class IterativeLoopTask(Task):
    def __init__(
        self,
        entrypoint,
        name,
        max_iterations=1,
        post_process=None,
        inputs=None,
        outputs=None,
    ):
        super().__init__()
        self.task_data = dict()
        self.name = name
        if outputs is not None:
            self._outputs = outputs
        else:
            self._outputs = ["iter_loop_result"]
        if post_process is not None:
            self.post_process = post_process
        else:
            self.post_process = lambda x: {outputs[0]: x}
        self.actor_init_kwargs = {
            "entrypoint": entrypoint,
            "post_process": self.post_process,
            "max_iterations": max_iterations,
            "outputs": outputs,
            # "break_func": self.break_func
        }

        self._inputs = inputs
        if outputs is not None:
            self._outputs += outputs

        self.actor_class = IterativeLoopActor
