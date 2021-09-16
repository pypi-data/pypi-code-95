import logging
import graphio
from typing import List, Dict, Type, Union, Tuple, Set, TYPE_CHECKING
from ..worker_base import WorkerBase, Progress
from .manager_workers_base import ManagerWorkersBase
from ..cache_backend import (
    NodeSetMeta,
    RelationSetMeta,
    SetsMetaBase,
)

if TYPE_CHECKING:
    from .manager import Manager

log = logging.getLogger(__name__)


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

    def manage(self):
        c = self.parent.strategy.amount_loading_nodes_cores()
        self.manage_nodeset_loading(c)
        c = self.parent.strategy.amount_loading_rels_cores()
        self.manage_relation_loading(c)

    def is_done(self):
        # we are done when:
        # sourcing is finished and there is no more data in the cache...
        if (
            self.parent.manager_sourcing.is_done()
            and not self.parent.cache.list_SetsMeta()
        ):
            # ... and all workers are finished
            if (
                len(self._get_workers(status="running"))
                + len(self._get_workers(status="initial"))
                == 0
            ):
                return True
        else:
            return False

    def manage_nodeset_loading(self, assigned_no_of_cores):
        log.debug("###MANAGE NODESETS###")
        cached_sets = self.parent.cache.list_SetsMeta(set_type=graphio.NodeSet)
        # find NodeSets that have workers assigned (allready running or queued)
        cached_sets_worked_on: List[SetsMetaBase] = [
            worker.set_meta
            for worker in self._get_workers(
                progress=(Progress.QUEUED, Progress.LOADING),
                tag=self.worker_tag_nodesets,
            )
        ]
        # find nodeSets types that are not loaded atm
        cached_sets_not_worked_on: List[SetsMetaBase] = [
            cs for cs in cached_sets if cs not in cached_sets_worked_on
        ]
        # Collect nodeSets that are not allready loading and that are not blocked. These are the NodeSet types we can tackle next
        cached_sets_not_worked_on_and_not_blocked: List[SetsMetaBase] = [
            cs
            for cs in cached_sets_not_worked_on
            if not self.parent._is_nodeset_loading_blocked(cs)
        ]
        if cached_sets_not_worked_on_and_not_blocked:

            no_of_free_cores = assigned_no_of_cores - len(
                self._get_workers(status="running", tag=self.worker_tag_nodesets)
            )

            if no_of_free_cores < 0:
                no_of_free_cores = 0
            chached_sets_next = cached_sets_not_worked_on_and_not_blocked[
                :no_of_free_cores
            ]

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

        #
        # log.info(f"no_of_free_cores: {no_of_free_cores}/{assigned_no_of_cores}")

        # start new workers:
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
            # break

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
