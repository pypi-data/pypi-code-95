# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from outflow.core.db import Model
from outflow.management.models.mixins import Executable
from outflow.management.models.run import Run
from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship


class Task(Model, Executable):
    """
    Stores the tasks
    """

    id = Column(Integer, primary_key=True, nullable=False)
    plugin = Column(String(256), nullable=True)
    name = Column(String(256), nullable=False)
    run_id = Column(Integer, ForeignKey(Run.id), nullable=False)
    run = relationship("Run")
    input_targets = Column(JSON, nullable=False, server_default="{}")
    output_targets = Column(JSON, nullable=False, server_default="{}")
    upstream_tasks = relationship(
        "Task",
        secondary="edge",
        primaryjoin="Task.id == Edge.downstream_task_id",
        secondaryjoin="Task.id == Edge.upstream_task_id",
        backref="downstream_tasks",
    )
    workflow_id = Column(Integer, ForeignKey("workflow.id"), nullable=False)
    workflow = relationship(
        "Workflow", back_populates="tasks", foreign_keys=[workflow_id]
    )


class Edge(Model):
    """
    Stores relations between tasks
    """

    upstream_task_id = Column(Integer, ForeignKey(Task.id), primary_key=True)
    downstream_task_id = Column(Integer, ForeignKey(Task.id), primary_key=True)
