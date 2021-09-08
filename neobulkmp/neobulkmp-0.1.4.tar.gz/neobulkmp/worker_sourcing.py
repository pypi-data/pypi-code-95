import graphio
from typing import Callable, Any, Union, Generator, Dict
from .worker_base import WorkerBase
from logging import Logger
from .cache_backend import CacheInterface
import time


class WorkerSourcing(WorkerBase):
    sourcing_func: Callable[
        [Any], Generator[Union[graphio.NodeSet, graphio.RelationshipSet], None, None]
    ] = None

    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.worker_parameter = kwargs

    def run(self):
        self.cache: CacheInterface = self.cache_backend(self.cache_backend_params)

        log: Logger = self.get_logger()
        log.debug(f"START {self.name}")
        if not isinstance(self.worker_parameter, dict):
            raise ValueError("worker_parameter not a dict:", self.worker_parameter)
        for set in self.sourcing_func(**self.worker_parameter):
            data_stored = False
            while not data_stored:
                if self.cache.store_is_available():
                    if isinstance(set, graphio.NodeSet):
                        log.debug(f"Recieved graphio.NodeSet '{set.labels}'")
                        self.cache.store_NodeSet(set)
                    elif isinstance(set, graphio.RelationshipSet):
                        log.debug(f"Recieved graphio.RelationshipSet '{set.rel_type}'")
                        self.cache.store_RelSet(set)
                    else:
                        raise ValueError(
                            f"Worker '{self.name}' yielded wrong type of data. Expected 'graphio.NodeSet' or 'graphio.RelationshipSet' got '{type(set)}' "
                        )
                    data_stored = True
                else:
                    # wait 10 second for store to open again and try again
                    time.sleep(10)
