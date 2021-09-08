# -*- coding: utf-8 -*-
from copy import deepcopy

from outflow.library.tasks.base_map_task import BaseMapTask


class SequentialMapTask(BaseMapTask):
    def run(self, **map_inputs):

        results = list()

        for index, generated_inputs in enumerate(self.generator(**map_inputs)):
            if index == 0:
                workflow_copy = self.inner_workflow
            else:
                workflow_copy = deepcopy(self.inner_workflow)

            results.append(
                self.run_workflow(
                    workflow_copy,
                    generated_inputs,
                    index,
                    self.raise_exceptions,
                    self.external_edges,
                )
            )

        return self.reduce(results)
