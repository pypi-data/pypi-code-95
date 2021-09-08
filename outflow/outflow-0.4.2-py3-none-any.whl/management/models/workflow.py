# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from outflow.core.db import Model
from outflow.management.models.run import Run
from outflow.management.models.task import Task


class Workflow(Model):
    """
    Stores a workflow
    """

    id = Column(Integer, primary_key=True)
    manager_task_id = Column(Integer, ForeignKey(Task.id), nullable=True)
    manager_task = relationship("Task", foreign_keys=[manager_task_id])
    parent_workflow_id = Column(Integer, ForeignKey("workflow.id"), nullable=True)
    parent_workflow = relationship("Workflow")
    run_id = Column(Integer, ForeignKey(Run.id), nullable=False)

    run = relationship("Run")

    tasks = relationship("Task", foreign_keys="Task.workflow_id")
