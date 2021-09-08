# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy.orm import relationship

from outflow.core.db import Model


class Configuration(Model):
    """
    Stores a run configuration
    """

    id = Column(Integer, primary_key=True)
    config = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=False)
    hash = Column(String(64), nullable=False, unique=True)
    runs = relationship("Run", back_populates="configuration")
