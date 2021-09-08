# -*- coding: utf-8 -*-
from outflow.core.pipeline import get_pipeline_states
from outflow.core.tasks import Task
from outflow.ray.remote_run import remote_run


class ParallelTask(Task):
    def __init__(self):
        super().__init__()

    def _run(self, *args, **kwargs):

        object_ref = remote_run.remote(
            self.run,
            pipeline_states=get_pipeline_states(),
            **kwargs,
            **self.bind_kwargs,
            **self.parameterized_kwargs
        )

        return object_ref

    def check_return_type(self, return_value):
        pass
