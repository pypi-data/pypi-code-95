# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from outflow.core.db import Model
from outflow.management.models.task import Task


class RuntimeException(Model):
    """
    This table provides the history of the runtime exceptions that
    occurred in the pipeline.
    """

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey(Task.id))
    exception_type = Column(String(64), nullable=False)
    exception_msg = Column(Text, nullable=False)
    traceback = Column(Text, nullable=False)
    task = relationship("Task")
    time = Column(DateTime, nullable=False)
