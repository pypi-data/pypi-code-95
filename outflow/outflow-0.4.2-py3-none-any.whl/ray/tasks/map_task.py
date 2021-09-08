# -*- coding: utf-8 -*-
import ray

from outflow.library.tasks.base_map_task import BaseMapTask
from outflow.core.pipeline import get_pipeline_states
from outflow.ray.remote_run import remote_run


class ParallelMapTask(BaseMapTask):
    def __init__(self, *args, num_cpus=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_cpus = num_cpus

    def run(self, **map_inputs):

        workflow_results_refs = list()

        for index, generated_inputs in enumerate(self.generator(**map_inputs)):
            workflow_result_ref = remote_run.options(num_cpus=self.num_cpus).remote(
                # ray remote args
                self.run_workflow,
                # run_workflow args
                pipeline_states=get_pipeline_states(),
                workflow=self.inner_workflow,
                inputs=generated_inputs,
                index=index,
                raise_exceptions=self.raise_exceptions,
                external_edges=self.external_edges,
            )

            workflow_results_refs.append(workflow_result_ref)

        return self.reduce(ray.get(workflow_results_refs))
