#!/usr/bin/env python
# -*- coding: utf-8 -*--
import logging
logger = logging.getLogger(__name__)

# TODO remove
import mlx

from .mlx_global_explainer import *
from .mlx_local_explainer import *

mlx.initjs()
