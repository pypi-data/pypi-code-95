# -*- coding: utf-8 -*-
from outflow.core.generic.lazy_object_proxy import LazyObjectProxy
from outflow.core.logging import logger
from outflow.core.pipeline import context
from outflow.library.tasks.sequential_map_task import SequentialMapTask
from outflow.ray.tasks.map_task import ParallelMapTask


def determine_map_class():
    logger.debug(f"Generic MapTask initializing a {context.backend_name} MapTask")

    if context.backend_name == "default":
        return SequentialMapTask
    elif context.backend_name == "ray":
        return ParallelMapTask
    else:
        raise AttributeError("Could not determine backend for generic MapTask")


MapTask = LazyObjectProxy(determine_map_class)
