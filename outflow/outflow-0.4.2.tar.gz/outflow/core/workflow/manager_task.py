# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4

from outflow.core.workflow.workflow_manager import WorkflowManager


class ManagerTask:
    """
    Make a Task usable as a context manager, to create a subworkflow

    Must be use as a mixin with the class Task
    """

    def __init__(self):
        self.external_edges = {}

    def __enter__(self):
        self.workflow_manager = WorkflowManager().__enter__(manager_task=self)
        self.inner_workflow = self.workflow_manager.get_context()["workflow"]

        return self

    def __exit__(self, *args):

        self.workflow_manager.__exit__(*args)
        self.workflow_manager = None

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        map_task_copy = cls.__new__(cls)
        memodict[id(self)] = map_task_copy
        for k, v in self.__dict__.items():
            if k not in ["inner_workflow", "workflow_manager", "workflow", "uuid"]:
                setattr(map_task_copy, k, deepcopy(v, memodict))
        map_task_copy.workflow = self.workflow
        map_task_copy.uuid = uuid4()
        map_task_copy.workflow_manager = self.workflow_manager
        map_task_copy.inner_workflow = self.inner_workflow
        return map_task_copy

    def add_external_edge(self, parent_task, child_task):
        self.external_edges.update({parent_task: child_task})
        parent_task.add_child(self, save_in_db=False)

    @staticmethod
    def setup_external_edges(workflow, external_edges, inputs_copy):
        internal_tasks_inputs = {}
        for external_task, internal_task in external_edges.items():
            external_task_inputs = {}
            for output_name in external_task.outputs:
                external_task_inputs.update({output_name: inputs_copy[output_name]})
                del inputs_copy[output_name]

            internal_tasks_inputs.update({internal_task: external_task_inputs})

        for internal_task, external_inputs in internal_tasks_inputs.items():
            real_internal_task = [
                task for task in workflow if task.name == internal_task.name
            ][0]
            real_internal_task.bind(**external_inputs)
