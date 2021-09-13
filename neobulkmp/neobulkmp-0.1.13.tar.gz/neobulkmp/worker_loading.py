import time
import graphio
import traceback
from py2neo import Graph
from typing import Dict
from .worker_base import WorkerBase
from .cache_backend import CacheInterface, SetsMetaBase
from linetimer import CodeTimer


class WorkerLoading(WorkerBase):
    def __init__(
        self,
        name,
        set_meta: SetsMetaBase,
        graph_params: Dict,
        insert_action: str = "create",
        create_index: bool = True,
        create_unique_constraints: bool = False,
        amount_of_retries_on_loading_fail: int = 4,
    ):
        super(type(self), self).__init__()
        self.name: str = name
        self.set_meta: SetsMetaBase = set_meta
        self.graph_params: Dict = graph_params
        self.insert_action: str = insert_action
        self.create_index = create_index
        self.create_unique_constraints = create_unique_constraints
        self.drain_order_ticket = None
        self.amount_of_retries_on_loading_fail = amount_of_retries_on_loading_fail

    def run(self):
        super(type(self), self).run()
        self.cache: CacheInterface = self.cache_backend(self.cache_backend_params)
        graph_set = None
        log = self.get_logger()
        log.info(f"START {self.name}")
        try:
            timer = CodeTimer(unit="s", silent=True)
            if self.set_meta.type == graphio.NodeSet:
                with timer:
                    graph_set = self.cache.fetch_NodeSets(self.set_meta)
                log.debug(
                    f"Fetched NodeSet with {len(graph_set.nodes)} Nodes from cache in {timer.took} sec."
                )
            elif self.set_meta.type == graphio.RelationshipSet:
                with timer:
                    graph_set = self.cache.fetch_RelSets(
                        self.set_meta, self.drain_order_ticket
                    )
                log.debug(
                    f"Fetched RelationshipSet with {len(graph_set.relationships)} Relations in {timer.took} sec."
                )
            else:
                log.error(
                    f"Wrong meta data for set. Expected <graphio.NodeSet> or <graphio.RelationshipSet> got {self.set_meta.type}"
                )
                raise ValueError(
                    f"Wrong meta data for set. Expected <graphio.NodeSet> or <graphio.RelationshipSet> got {self.set_meta.type}"
                )
        except Exception as e:
            log.error(traceback.format_exc())
            raise e
        loading_attempt_count = 0
        loading_finished = False
        while not loading_finished:
            try:
                g = Graph(**self.graph_params)
                timer = CodeTimer(unit="s", silent=True)
                if self.create_index:
                    log.debug(f"Create index for {graph_set}")
                    graph_set.create_index(g)
                if self.create_unique_constraints:
                    log.debug(f"Create unique constraint for {graph_set}")
                    raise NotImplementedError
                if self.insert_action == "create":
                    with timer:
                        graph_set.create(g)
                    log.debug(f"Created {graph_set} into DB in {timer.took} sec")
                elif self.insert_action == "merge":
                    with timer:
                        graph_set.merge(g)
                    log.debug(f"Merged {graph_set} into DB in {timer.took} sec")
                else:
                    m = f"Unknown insert action. Expected 'create' or 'merge' got '{self.insert_action}'"
                    log.error(m)
                    raise ValueError(m)
                # log loading stats
                if isinstance(graph_set, graphio.NodeSet):
                    amount = f"{len(graph_set.nodes)} nodes"
                    name = f'({":".join(graph_set.labels)})'
                else:
                    amount = f"{len(graph_set.relationships)} relations"
                    name = f"{graph_set.rel_type}"
                log.info(f"Loaded {name} with {amount} into DB in {timer.took} sec")
                loading_finished = True
            except Exception as e:
                if loading_attempt_count >= self.amount_of_retries_on_loading_fail:
                    log.exception(
                        f"Failed to insert after {loading_attempt_count} tries: {self.set_meta}"
                    )
                    raise e
                loading_attempt_count += 1
                log.warning(
                    f"Failed to {self.insert_action} into neo4j@{self.graph_params} with error \n {str(e)}\n. Will retry {self.amount_of_retries_on_loading_fail - loading_attempt_count} times..."
                )
                time.sleep(10)

        self.cache.report_SetLoaded(graph_set)
