import multiprocessing
from .cache_backend import CacheInterface
from typing import Dict, List
from linetimer import CodeTimer
from .cache_logger import CacheLoggerHandler
import logging
import uuid


class WorkerBase(multiprocessing.Process):
    cache_backend: CacheInterface = None
    cache_backend_params: Dict = None

    def __init__(self):
        super(WorkerBase, self).__init__()
        self.tags: List[str] = []
        self.params: Dict = {}
        self.timer: CodeTimer = CodeTimer(silent=True, unit="s")
        self.cache: CacheInterface = None
        self.id: str = uuid.uuid4().hex
        self.progress = "queued"

    def run(self):
        pass

    def get_logger(self) -> logging.Logger:
        if self.cache:
            logging.basicConfig(level=logging.INFO, handlers=[])
            log = logging.getLogger(self.name)
            log.addHandler(CacheLoggerHandler(self.cache))
            return log
        else:
            raise KeyError(
                "WorkerBase self.cache is None. Initate cache backed first before call 'get_logger'"
            )
