#!/usr/bin/env python

__all__ = []

import logging

from .catalogs import Catalog

logger = logging.getLogger(__name__)

#  TODO list and give access to whole services and their beta/alpha / pre-prod instances if existing

oidb = Catalog("oidb")
