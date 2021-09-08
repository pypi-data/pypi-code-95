# -*- coding: utf-8 -*-
from outflow.core.generic.context_manager import ContextManager
from outflow.core.workflow.workflow import Workflow


class WorkflowManager(ContextManager):
    def __enter__(self, manager_task=None):
        super().__enter__()
        if self.parent_context:
            workflow = Workflow(
                manager_task=manager_task,
                parent_workflow=self.parent_context["workflow"],
            )
        else:
            workflow = Workflow()

        self._context["workflow"] = workflow

        return self
