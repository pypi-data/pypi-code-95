import multiprocessing
import logging
from multiprocessing.context import ProcessError
import operator
import graphio
import json
import time
from linetimer import CodeTimer
from typing import List, Dict, Type, Set, Union, Tuple
from .worker_base import WorkerBase
from .worker_sourcing import WorkerSourcing
from .worker_loading import WorkerLoading
from .cache_backend import (
    CacheInterface,
    NodeSetMeta,
    RedisCache,
    RelationSetMeta,
    SetsMetaBase,
)
from .manager_strategies import StrategyBase
from .cache_logger import LogRecordStreamHandler
import humanfriendly
from enum import Enum


### DEBUG1
import graphio
from .cache_backend import RedisCache

###/DEBUG1


log = logging.getLogger(__name__)


class Progress(str, Enum):
    # str mixin, to be able to compare enums to strings. cool trick! see https://stackoverflow.com/a/63028809/12438690
    QUEUED = "queued"
    DRAIN_ORDERED = "drain"
    DRAIN_READY = "drained"
    LOADING = "load"
    COMPLETE = "complete"


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
            cache_size (str, optional): Max size of cache that should be available in humanfriendly ( https://pypi.org/project/humanfriendly/ ) format . Defaults to "500MB".
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
        self.strategy: StrategyBase = self.strategy_type(self)
        self.insert_action: str = "create"
        self.create_indexes = True
        self.create_unique_constraints = False
        self.worker_logging_reciever = LogRecordStreamHandler(self.cache)
        self.cache_size = humanfriendly.parse_size(cache_size)

        self.blocked_labels: Dict[str, Set[SetsMetaBase]] = {}

        self.status_log_every_n_sec = 3

        # DEBUG1
        self.NODESETS_DONE = []
        # /DEBUG1

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
        self.manager_sourcing = ManagerWorkersSourcing(self, self.worker_sourcing_class)
        self.manager_loading = ManagerWorkersLoading(self, self.worker_loading_class)

        finished = False
        self.worker_logging_reciever.handle()
        log.info("##Management start##")
        last_status_log_time = time.time()
        while not finished:
            if time.time() - last_status_log_time > self.status_log_every_n_sec:
                self.log_status()
                last_status_log_time -= time.time()

            log.debug(f"blocked_labels: {self.blocked_labels}")
            self.manager_sourcing.manage()
            self.manager_loading.manage()
            finished = (
                self.manager_sourcing.is_done() and self.manager_loading.is_done()
            )
            # Tiny pause until next management tick
            time.sleep(0.05)
        log.debug("##Management finish##")
        # Wait for all log records to be processed
        while not self.is_cache_log_flushed():
            time.sleep(0.1)

    def log_status(self):

        sourcing_worker_running_count = len(
            self.manager_sourcing._get_workers(status="running")
        )
        sourcing_worker_finished_count = len(
            self.manager_sourcing._get_workers(progress=Progress.COMPLETE)
        )
        sourcing_core_count = self.strategy.amount_sourcing_cores()

        loading_rels_worker_count = len(
            self.manager_loading._get_workers(
                status="running", tag=self.manager_loading.worker_tag_relsets
            )
        )
        waiting_rels_worker_count = len(
            self.manager_loading._get_workers(
                progress=Progress.DRAIN_ORDERED,
                tag=self.manager_loading.worker_tag_relsets,
            )
        )
        loading_rels_core_counts = self.strategy.amount_loading_rels_cores()

        loading_nodes_worker_count = len(
            self.manager_loading._get_workers(
                progress=(Progress.QUEUED, Progress.LOADING),
                tag=self.manager_loading.worker_tag_nodesets,
            )
        )
        loading_nodes_core_counts = self.strategy.amount_loading_nodes_cores()

        cache_storage_level = self.strategy._get_cache_storage_level()
        cache_storage_level_data = f"{int(100 - ((self.strategy._get_cache_storage_used() * 100) / self.strategy._get_cache_storage_total()))}% Free ({humanfriendly.format_size(self.strategy._get_cache_storage_used())} used of {humanfriendly.format_size(self.strategy._get_cache_storage_total())})"

        log.info(
            f"######STATUS######\n"
            + f"# Sourcing (Cores available {self.strategy.amount_sourcing_cores()})\n"
            + f"\tRunning sourcing workers {sourcing_worker_running_count} with {sourcing_core_count} cores\n"
            + f"\tFinished sourcing workers {sourcing_worker_finished_count} of {len(self.manager_sourcing.workers)}\n"
            + f"# Loading (Cores available {self.strategy.amount_loading_cores()})\n"
            + f"\tRunning RelationshipSet workers {loading_rels_worker_count} with {loading_rels_core_counts} cores\n"
            + f"\tWaiting for drain RelationshipSet workers {waiting_rels_worker_count} with {loading_rels_core_counts} cores\n"
            + f"\tRunning/Queded NodeSet workers {loading_nodes_worker_count} with {loading_nodes_core_counts} cores\n"
            + f"# Cache\n"
            + f"\tRelationSet count in cache: {len(self.cache.list_SetsMeta(graphio.RelationshipSet))}\n"
            + f"\tRelationSet size in cache: {humanfriendly.format_size(self.strategy._get_cache_storage_used_by_relSets())}\n"
            + f"\tNodeSet count in cache: {len(self.cache.list_SetsMeta(graphio.NodeSet))}\n"
            + f"\tNodeSet size in cache: {humanfriendly.format_size(self.strategy._get_cache_storage_used_by_nodeSets())}\n"
            + f"\tLabels blocked for RelationSet loading count: {len(self._get_blocked_labels())}\n"
            + f"\tCache storage level: {cache_storage_level} - {cache_storage_level_data}\n"
            + f"# Memory\n"
            + f"\tMemory level: {humanfriendly.format_size(self.strategy._get_memory_available())} available - {humanfriendly.format_size(self.strategy._get_memory_used())} used of {humanfriendly.format_size(self.strategy._get_memory_total())}\n"
            + f"\tMemory consumed by parsers {humanfriendly.format_size(self.strategy._get_memory_consumed_by_parsers())}\n"
            + f"\tMemory consumed by loaders {humanfriendly.format_size(self.strategy._get_memory_consumed_by_loaders())}\n"
            + f"\tMemory consumed by manager {humanfriendly.format_size(self.strategy._get_memory_consumed_by_manager())}\n"
        )

        ### DEBUG1

        log.info(f"# NODESET DONE:\n{self.NODESETS_DONE}\n")
        log.info(
            f"# NODESETS WITH DRAIN ORDER:\n{RedisCache.DrainOrder.list_open_nodesets_meta(self.cache)}\n"
        )

        log.info(
            f"# OVERLAP COUNT {len(list(set(self.NODESETS_DONE) & set(RedisCache.DrainOrder.list_open_nodesets_meta(self.cache))))}\n"
        )

        self.NODESETS_DONE = []

        ###/DEBUG1

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
        # if 90% of memory is occupied we dont allow any more soursing workers to store data
        if self.strategy.memory_level() == "RED":
            self.cache_backend.close_store()
            log.warning(
                "Cache backend is blocked for storing new NodeSets and RelationshipSets due to low memory. \n This will impact the overall perfomance dramaticly, but prevents the process from crashing. \n Try to work with a lower core count or get more memory."
            )
        elif not self.cache_backend.store_is_available():
            self.cache_backend.open_store()
            log.info(
                "Cache backend is open for storing NodeSets and RelationshipSets again"
            )


class ManagerWorkersBase:
    parent: Manager = None
    worker_class: Type[WorkerBase] = None

    def __init__(self, manager: "Manager", worker_class: Type[WorkerBase]):
        self.parent = manager
        self.workers: List[WorkerBase] = []
        self.finished_workers: List[WorkerBase] = []
        self.failed_workers: List[WorkerBase] = []
        self.worker_class = worker_class

        # Setup caching backend on worker class

        self.worker_class.cache_backend = self.parent.cache_backend
        self.worker_class.cache_backend_params = self.parent.cache_backend_params

    def is_done(self):
        raise NotImplementedError

    def _get_process_status(self, worker):
        if worker.is_alive():
            return "running"
        else:
            if worker.exitcode is None:
                return "initial"
            elif worker.exitcode == 0 and worker not in self.finished_workers:
                return "exited"
            elif worker.exitcode != 0 and worker not in self.failed_workers:
                return "failed"
            elif worker in self.finished_workers + self.failed_workers:
                return "closed"
        raise ValueError(
            "Could not determine process status. Something went wrong",
            worker.exitcode,
            worker,
        )

    def _init_workers(
        self, parameters: List[Dict], names: List[str] = None, tags: List = None
    ):
        if not names:
            names = [hash(str(p)) for p in parameters]
        for name, params in zip(names, parameters):
            name = f"{self.worker_class.__name__}-{';'.join(tags or [])}-{name}"
            w: WorkerBase = self.worker_class(name=name, **params)
            log.debug(f"INIT WORKER {w.name}")
            w.tags = tags
            w.params = params
            self.workers.append(w)

    def _finish_workers(self, tag: str = None) -> bool:
        did_any_workers_finish = False
        for fin_worker in self._get_workers("exited", tag=tag):
            did_any_workers_finish = True
            fin_worker.join()
            fin_worker.timer.__exit__(None, None, None)
            self.parent._release_loading_block_label(fin_worker.id)
            fin_worker.progress = Progress.COMPLETE
            self.finished_workers.append(fin_worker)

            # DEBUG1
            import graphio

            if hasattr(fin_worker, "set_meta"):
                set_meta: SetsMetaBase = fin_worker.set_meta
                if set_meta.type == graphio.NodeSet:
                    self.parent.NODESETS_DONE.append(set_meta)
            # /DEBUG1

            log.debug(f"Exit worker '{fin_worker.name}'")
        # Exit failed worker
        for fail_worker in self._get_workers("failed", tag=tag):
            did_any_workers_finish = True
            fail_worker.join()
            fail_worker.timer.__exit__(None, None, None)
            # release any nodeset blocks
            self.parent.blocked_labels.pop(fail_worker.id, None)
            self.failed_workers.append(fail_worker)
            self.parent._release_loading_block_label(fail_worker.id)
            fail_worker.progress = Progress.COMPLETE
            log.error(
                f"Exit failed worker '{fail_worker.name}' \n other workers currently running are {self._get_workers('running')}"
            )
            raise ProcessError(f"'{fail_worker.name}' failed")
        return did_any_workers_finish

    def _get_workers(
        self,
        status: Union[str, List, Tuple, Set] = None,
        progress: Union[str, List, Tuple, Set] = None,
        tag=None,
    ):
        return [
            w
            for w in self.workers
            if (tag is None or tag in w.tags)
            and (
                status is None
                or (isinstance(status, str) and self._get_process_status(w) == status)
                or (
                    isinstance(status, (list, set, tuple))
                    and self._get_process_status(w) in status
                )
            )
            and (
                progress is None
                or (isinstance(progress, str) and w.progress == progress)
                or (isinstance(progress, (list, set, tuple)) and w.progress in progress)
            )
        ]


class ManagerWorkersSourcing(ManagerWorkersBase):
    def __init__(self, manager: "Manager", worker_class: Type[WorkerBase]):
        super(type(self), self).__init__(manager, worker_class)
        # create workers distribute task parameters per worker
        log.debug(f"self.parent.worker_parameters: {self.parent.worker_parameters}")
        self._init_workers(parameters=self.parent.worker_parameters)
        self.worker_count_total = len(self.workers)

    def is_done(self):
        # Mom, Are We There Yet?
        if len(self.workers) == len(self._get_workers(status="closed")):
            return True
        else:
            return False

    def manage(self):
        available_cores = self.parent.strategy.amount_sourcing_cores()
        # Collect all running sourcing workers
        waiting_workers = self._get_workers(status="initial")
        new_worker_started = False
        # Start next worker
        if (
            len(self._get_workers(status="running")) < available_cores
            and len(waiting_workers) > 0
        ):
            new_worker_started = True
            next_worker = waiting_workers.pop(0)
            log.debug(f"CALL START ON SOURCING {next_worker} - {next_worker.params}")
            next_worker.start()
            next_worker.timer.__enter__()

        workers_did_finished = self._finish_workers()
        if workers_did_finished or new_worker_started:
            log.debug(
                f"SOURCING: {len(self.finished_workers) + len(self.failed_workers)} Workers finished / {len(self._get_workers('running'))} Workers running / {len(self._get_workers('initial'))} Workers waiting / {len(self.failed_workers)} Workers failed / {available_cores} Max sourcing workers running simultaneously"
            )


class ManagerWorkersLoading(ManagerWorkersBase):
    def __init__(self, manager: "Manager", worker_class: Type[WorkerBase]):
        super(type(self), self).__init__(manager, worker_class)
        self.parent = manager

        # Setup caching backend on worker class
        self.parent.worker_loading_class.cache_backend = self.parent.cache_backend
        self.parent.worker_loading_class.cache_backend_params = (
            self.parent.cache_backend_params
        )
        self.worker_tag_relsets = "RELSET"
        self.worker_tag_nodesets = "NODESET"

    def is_done(self):
        # we are done when:
        # sourcing is finished and there is no more data in the cache...
        if (
            self.parent.manager_sourcing.is_done()
            and not self.parent.cache.list_SetsMeta()
        ):
            # ... and all workers are finished
            if (
                len(self._get_workers("running")) + len(self._get_workers("initial"))
                == 0
            ):
                return True
        else:
            return False

    def manage_nodeset_loading(self, assigned_no_of_cores):
        log.debug("###MANAGE NODESETS###")
        cached_sets = self.parent.cache.list_SetsMeta(set_type=graphio.NodeSet)
        log.debug(f"len(cached_sets): {len(cached_sets)}")
        # find NodeSets that have workers assigned (allready running or queued)
        cached_sets_worked_on: List[SetsMetaBase] = [
            worker.set_meta
            for worker in self._get_workers(
                progress=(Progress.QUEUED, Progress.LOADING),
                tag=self.worker_tag_nodesets,
            )
        ]
        log.debug(f"len(cached_sets_worked_on): {len(cached_sets_worked_on)}")
        # find nodeSets types that are not loaded atm
        cached_sets_not_worked_on: List[SetsMetaBase] = [
            cs for cs in cached_sets if cs not in cached_sets_worked_on
        ]
        log.debug(f"len(cached_sets_not_worked_on): {len(cached_sets_not_worked_on)}")
        # Collect nodeSets that are not allready loading and that are not blocked. These are the NodeSet types we can tackle next
        cached_sets_not_worked_on_and_not_blocked: List[SetsMetaBase] = [
            cs
            for cs in cached_sets_not_worked_on
            if not self.parent._is_nodeset_loading_blocked(cs)
        ]
        log.debug(
            f"len(cached_sets_not_worked_on_and_not_blocked): {len(cached_sets_not_worked_on_and_not_blocked)}"
        )
        log.debug(f"Labels blocked: {self.parent._get_blocked_labels()}")
        if cached_sets_not_worked_on_and_not_blocked:

            no_of_free_cores = assigned_no_of_cores - len(
                self._get_workers(status="running", tag=self.worker_tag_nodesets)
            )

            log.debug(f"no_of_free_cores {no_of_free_cores}")
            if no_of_free_cores < 0:
                no_of_free_cores = 0
            chached_sets_next = cached_sets_not_worked_on_and_not_blocked[
                :no_of_free_cores
            ]

            log.debug(f"chached_sets_next {len(chached_sets_next)} {chached_sets_next}")
            # Prepare parameter to initialize workers
            workers_params: List[Dict] = [
                {
                    "set_meta": cached_set_meta,
                    "graph_params": self.parent.graph_params,
                    "insert_action": self.parent.insert_action,
                    "create_index": self.parent.create_indexes,
                    "create_unique_constraints": self.parent.create_unique_constraints,
                }
                for cached_set_meta in chached_sets_next
            ]
            # generate human readable names for workers
            worker_names: List[str] = [
                ":".join(self.parent.cache.get_NodeSetMeta(cached_set_meta).labels)
                for cached_set_meta in chached_sets_next
            ]
            # Initialize new workers
            self._init_workers(
                parameters=workers_params,
                names=worker_names,
                tags=[self.worker_tag_nodesets],
            )
        no_of_free_cores = assigned_no_of_cores - len(
            self._get_workers(status="running", tag=self.worker_tag_nodesets)
        )

        log.debug(f"no_of_free_cores: {no_of_free_cores}")

        # start new workers:
        log.debug(
            f"len(self._get_workers(progress=Progress.QUEUED, tag=self.worker_tag_nodesets) {len(self._get_workers(progress=Progress.QUEUED, tag=self.worker_tag_nodesets))}"
        )
        for next_worker in self._get_workers(
            progress=Progress.QUEUED, tag=self.worker_tag_nodesets
        ):
            next_worker.progress = Progress.LOADING
            next_worker.timer.__enter__()
            next_worker.start()

        # collect exited workers
        workers_did_finished = self._finish_workers(self.worker_tag_nodesets)

    def manage_relation_loading(self, assigned_no_of_cores):
        log.debug(
            f"Manage Relsets loading with {assigned_no_of_cores} cores available"
            + f" and {len(self._get_workers(status='running',tag=self.worker_tag_relsets))} worker running atm."
            + f" {len(self._get_workers(progress=Progress.DRAIN_ORDERED, tag=self.worker_tag_relsets))} workers are waiting for a drain"
        )
        log.debug(
            f"DRAINING WAIT: {self._get_workers(progress=Progress.DRAIN_ORDERED, tag=self.worker_tag_relsets)}"
        )

        cached_sets = self.parent.cache.list_SetsMeta(set_type=graphio.RelationshipSet)

        # find RelSets that have workers assigned (allready running or queued)
        cached_sets_worked_on: List[RelationSetMeta] = [
            self.parent.cache.get_RelSetMeta(worker.set_meta)
            for worker in self._get_workers(
                progress=(
                    Progress.QUEUED,
                    Progress.DRAIN_ORDERED,
                    Progress.DRAIN_READY,
                    Progress.LOADING,
                ),
                tag=self.worker_tag_relsets,
            )
        ]

        log.debug(
            f"Relations cached_sets_worked_on count: {len(cached_sets_worked_on)}"
        )
        if len(cached_sets_worked_on) < assigned_no_of_cores:
            cached_sets_not_worked_on: List[RelationSetMeta] = [
                self.parent.cache.get_RelSetMeta(cs)
                for cs in cached_sets
                if cs not in cached_sets_worked_on
            ]

            if cached_sets_not_worked_on:
                no_of_free_cores = assigned_no_of_cores - len(cached_sets_worked_on)
                cached_sets_next = []
                for next_set in cached_sets_not_worked_on:
                    # filter out overlapping nodesets, which could cause nodelocks
                    overlaps = False
                    # get target labels of the potential next relationship loader
                    next_ns_labels = (
                        next_set.end_node_labels + next_set.start_node_labels
                    )
                    # get all target labels that currently affected by running relationship loaders
                    current_ns_labels = {
                        label
                        for cs in cached_sets_worked_on + cached_sets_next
                        for label in cs.start_node_labels + cs.end_node_labels
                    }

                    for n_label in next_ns_labels:
                        if n_label in current_ns_labels:
                            overlaps = True

                    if not overlaps:
                        cached_sets_next.append(next_set)
                    if len(cached_sets_next) >= no_of_free_cores:
                        break

                # cached_sets_next = cached_sets_not_worked_on[:no_of_free_cores]
                # Prepare parameter and name list to initialize new workers
                workers_params: List[Dict] = [
                    {
                        "set_meta": cached_set_meta,
                        "graph_params": self.parent.graph_params,
                        "insert_action": self.parent.insert_action,
                        "create_index": self.parent.create_indexes,
                        "create_unique_constraints": self.parent.create_unique_constraints,
                    }
                    for cached_set_meta in cached_sets_next
                ]
                # generate human readable names for workers
                worker_names: List[str] = []
                for cached_set_meta in cached_sets_next:
                    worker_names.append(cached_set_meta.rel_type)
                # Initialize workers
                self._init_workers(
                    parameters=workers_params,
                    names=worker_names,
                    tags=[self.worker_tag_relsets],
                )

        # manage drain orders
        self._order_drains(assigned_no_of_cores)
        self._check_for_drains_ready(assigned_no_of_cores)

        # start one new worker per management tick
        for next_worker in self._get_workers(
            progress=Progress.DRAIN_READY, tag=self.worker_tag_relsets
        ):
            next_worker.progress = Progress.LOADING
            next_worker.timer.__enter__()
            log.debug(f"Start {next_worker.name}")
            next_worker.start()
            # we break the loop here as we only start one relationshipSet loader per management tick
            break

        # collect exited workers
        self._finish_workers(self.worker_tag_relsets)

    def _order_drains(self, assigned_no_of_cores):

        # Order drain for relationsSet attached NodeSets for next waiting worker

        next_relset_workers = [
            w
            for w in self._get_workers(
                progress=Progress.QUEUED, tag=self.worker_tag_relsets
            )
        ]
        for next_worker in next_relset_workers[:1]:
            drain_order_ticket_id = self.parent.cache.order_RelSetDrain(
                relset_meta=next_worker.set_meta
            )
            next_worker.progress = Progress.DRAIN_ORDERED
            next_worker.drain_order_ticket = drain_order_ticket_id

    def _check_for_drains_ready(self, assigned_no_of_cores):
        # Check if any running drains are ready
        for drain_wait_worker in self._get_workers(
            progress=Progress.DRAIN_ORDERED, tag=self.worker_tag_relsets
        ):
            if not self.parent.cache.is_drain_done(
                drain_wait_worker.drain_order_ticket
            ):
                # The drain is still running in the cache. we cant do anything atm
                # lets skip to the next relationSet
                continue

            # drain is ready: now we need to block new workers on our target nodesets labels and wait for running workers, that are loading our target nodeset types, to finish
            self.parent._block_loading_label(
                drain_wait_worker.id,
                set(
                    drain_wait_worker.set_meta.start_node_labels
                    + drain_wait_worker.set_meta.end_node_labels
                ),
            )

            # It can happen that workers, which were started before the drain order and are loading nodesets that are related to the relationshipSet, are still loading.
            # this means: there could be nodelocks when loading the relationshipSet or worse target nodes could be missing.
            # We need to make sure that there are no old running nodeset workers affecting/occupying our relationsship target nodesets
            nodesets_currently_worked_on: List[NodeSetMeta] = [
                self.parent.cache.get_NodeSetMeta(worker.set_meta)
                for worker in self._get_workers(
                    progress=(Progress.QUEUED, Progress.LOADING),
                    tag=self.worker_tag_nodesets,
                )
            ]
            labels_of_nodesets_currently_worked_on: Set[str] = {
                label for cs in nodesets_currently_worked_on for label in cs.labels
            }

            nodesets_occupied = False
            for label in (
                drain_wait_worker.set_meta.start_node_labels
                + drain_wait_worker.set_meta.end_node_labels
            ):
                if label in labels_of_nodesets_currently_worked_on:
                    # The drain ready but there are still other workers randomly working on this nodeset. we cant do anything atm
                    nodesets_occupied = True
            if nodesets_occupied:
                # lets skip to the next relationSet
                continue
            log.debug(
                f"DRAIN SEEMS READY drain_wait_worker.drain_order_ticket: {drain_wait_worker.drain_order_ticket}"
            )
            # Drain is ready and nothing is in the way of loading the relationshipset to the DB now. lets mark the worker as ready
            drain_wait_worker.progress = Progress.DRAIN_READY

    def manage(self):
        c = self.parent.strategy.amount_loading_nodes_cores()
        self.manage_nodeset_loading(c)
        c = self.parent.strategy.amount_loading_rels_cores()
        self.manage_relation_loading(c)
