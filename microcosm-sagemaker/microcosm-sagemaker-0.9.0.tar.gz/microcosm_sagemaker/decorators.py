from typing import Any, Callable

from microcosm.object_graph import ObjectGraph
from microcosm_logging.timing import elapsed_time


def training_initializer():
    """
    Register a microcosm component as a training initializer, so that its init
    method will automatically be called.  This function is designed to be used
    as a decorator on a factory.

    """
    def decorator(func: Callable[[ObjectGraph], Any]):
        def factory(graph):
            component = func(graph)
            graph.training_initializers.register(component)
            return component
        return factory
    return decorator


def metrics_observer():
    """
    Register a microcosm component as an experiment metric tracker,
    for it to get any metrics being logged.

    """
    def decorator(func: Callable[[ObjectGraph], Any]):
        def factory(graph):
            component = func(graph)
            graph.experiment_metrics.register(component)
            return component
        return factory
    return decorator


def _method_with_logging(original_method):
    def new_method(self, *args, **kwargs):
        self.logger.info(f"Started method `{original_method.__name__}`.")
        timing = {}
        with elapsed_time(timing):
            original_method(self, *args, **kwargs)
        self.logger.info(
            f"Completed method `{original_method.__name__}`"
            f"after {timing['elapsed_time']/1000:.3g} seconds."
        )
    return new_method


def log_bundle_methods(cls):

    _init = cls.__init__

    def __init__(self, graph: ObjectGraph, **kwargs) -> None:
        _init(self, graph, **kwargs)
        self._graph = graph

    cls.__init__ = __init__
    cls.fit = _method_with_logging(cls.fit)
    cls.load = _method_with_logging(cls.load)
    cls.save = _method_with_logging(cls.save)

    return cls
