import multiprocessing
import logging


import time
from typing import List, Dict, Type, Set, Union
from ..worker_sourcing import WorkerSourcing
from ..worker_loading import WorkerLoading
from ..cache_backend import (
    CacheInterface,
    NodeSetMeta,
    RedisCache,
    SetsMetaBase,
)
from .manager_workers_loading import ManagerWorkersLoading
from .manager_workers_sourcing import ManagerWorkersSourcing
from .manager_strategies import StrategyBase
from .manager_statistics import Statistics
from ..cache_logger import LogRecordStreamHandler
import humanfriendly


log = logging.getLogger(__name__)


class Manager:
    # Redis - Default cache backend

    strategy_type: Type[StrategyBase] = StrategyBase

    def __init__(
        self,
        worker_sourcing_class: Type[WorkerSourcing],
        worker_parameters: List[Dict],
        cache_backend: Type[CacheInterface] = RedisCache,
        cache_backend_params: Dict = None,
        cache_size: str = "2000MB",
        debug: bool = False,
    ):
        """[summary]

        Args:
            worker_sourcing_class (Type[WorkerSourcing]): [description]
            worker_parameters (List[Dict]): [description]
            cache_backend (Type[CacheInterface], optional): [description]. Defaults to RedisCache.
            cache_backend_params (Dict, optional): [description]. Defaults to None.
            cache_size (str, optional): Max size of cache that should be available in humanfriendly ( https://pypi.org/project/humanfriendly/ ) size format . Defaults to "2000MB".
        """
        self.debug = debug

        self.worker_sourcing_class = worker_sourcing_class
        self.worker_parameters = worker_parameters
        self.worker_loading_class = WorkerLoading
        self.graph_params = {}
        self.cpu_count: int = multiprocessing.cpu_count()
        self.cache_backend = cache_backend
        self.cache_backend_params = cache_backend_params
        self.cache: CacheInterface = self.cache_backend(
            self.cache_backend_params, debug=self.debug
        )
        self.statistics = Statistics(self)
        self.strategy: StrategyBase = self.strategy_type(self)
        self.insert_action: str = "create"
        self.create_indexes = True
        self.create_unique_constraints = False
        self.worker_logging_reciever = LogRecordStreamHandler(self.cache)
        self.cache_size = humanfriendly.parse_size(cache_size)

        self.blocked_labels: Dict[str, Set[SetsMetaBase]] = {}
        self.update_statistics_per_sec = 4
        self.status_log_every_n_sec = 8

    def test_cache_backend_ready(self):
        if self.cache.test_connection():
            return True
        else:
            return False

    def is_cache_log_flushed(self):
        if len(self.cache.get_logs()) == 0:
            return True
        else:
            return False

    def merge(self, graph_params: Dict = {}):
        self.graph_params = graph_params
        self.insert_action = "merge"
        self._start()

    def create(self, graph_params: Dict = {}):
        self.graph_params = graph_params
        self.insert_action = "create"
        self._start()

    def _start(self):
        if not self.test_cache_backend_ready():
            raise Exception(
                f"Cache backend {type(self.cache_backend)} {self.cache_backend_params} not available!"
            )
        self.cache.clear_cache()
        self.manager_sourcing = ManagerWorkersSourcing(self, self.worker_sourcing_class)
        self.manager_loading = ManagerWorkersLoading(self, self.worker_loading_class)
        self.management_ticks = 0
        finished = False
        self.worker_logging_reciever.handle()
        log.info("##Management start##")
        last_status_log_time = time.time()
        last_statistics_update = time.time()
        while not finished:
            self.management_ticks += 1
            if time.time() - last_status_log_time > self.status_log_every_n_sec:
                self.log_status()
                last_status_log_time = time.time()
            if time.time() - last_statistics_update > self.update_statistics_per_sec:
                self.statistics.update_statistics()
                last_statistics_update = time.time()

            log.debug(f"blocked_labels: {self.blocked_labels}")
            self.manager_sourcing.manage()
            self.manager_loading.manage()
            finished = (
                self.manager_sourcing.is_done() and self.manager_loading.is_done()
            )
        log.debug("##Management finish##")
        # Wait for all log records to be processed
        while not self.is_cache_log_flushed():
            time.sleep(0.1)
        self.statistics.update_statistics()
        log.info(self.statistics.get_human_readable_report())

    def log_status(self):
        log.info(self.statistics.get_human_readable_report())

    def _block_loading_label(self, block_id: str, labels: Set[str]):
        log.debug(f"BLOCK {labels}")
        if block_id in self.blocked_labels:
            self.blocked_labels[block_id].update(labels)
        else:
            self.blocked_labels[block_id] = set(labels)

    def _release_loading_block_label(self, block_id: str):
        self.blocked_labels.pop(block_id, None)

    def _is_nodeset_loading_blocked(
        self, nodeset_meta: Union[SetsMetaBase, NodeSetMeta]
    ) -> bool:
        if isinstance(nodeset_meta, SetsMetaBase):
            nodeset_meta: NodeSetMeta = self.cache.get_NodeSetMeta(nodeset_meta)
        for label in nodeset_meta.labels:
            if label in self._get_blocked_labels():
                return True

    def _get_blocked_labels(self) -> tuple:
        # flatten all values in a list and remove duplicates
        return {
            label for label_list in self.blocked_labels.values() for label in label_list
        }

    def _manage_store(self):
        # if 90% of memory is occupied we dont allow any more sourcing workers to store data
        if self.strategy.get_cache_storage_level() == "RED":
            self.cache_backend.close_store()
            log.warning(
                "Cache backend is blocked for storing new NodeSets and RelationshipSets due to low memory. \n This will impact the overall perfomance dramaticly, but prevents the process from crashing. \n Try to work with a lower core count or get more memory."
            )
        elif not self.cache_backend.store_is_available():
            self.cache_backend.open_store()
            log.info(
                "Cache backend is open for storing NodeSets and RelationshipSets again"
            )
