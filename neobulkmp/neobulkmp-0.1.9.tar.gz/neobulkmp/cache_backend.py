import os
import logging
import graphio
import json
import redis
import uuid
import operator
import time
import psutil
import jsonpickle
import traceback
from typing import Dict, Any, List, Type, Union, Generator

from dataclasses import dataclass, asdict

log = logging.getLogger(__name__)


class DrainNotReadyError(Exception):
    pass


@dataclass
class SetsMetaBase:
    """Metadata dataclass referencing a graphio.NodeSet or graphio.RelationshipSet in the cache."""

    # A key to reference the graphio set in the cache
    key: str
    # Size of the graphio set in the cache in bytes
    total_size_bytes: int
    # Indicator if the graphio set is a graphio.NodeSet or graphio.RelationshipSet
    type: Type = graphio.NodeSet

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.key == other.key:
            return True
        return False

    def __hash__(self):
        return hash(self.key)


@dataclass
class NodeSetMeta(SetsMetaBase):
    labels: List[str] = None
    # unused. to be removed:
    # relations: List[dict] = None


@dataclass
class RelationSetMeta(SetsMetaBase):
    type: Type = graphio.RelationshipSet
    end_node_labels: List[str] = None
    start_node_labels: List[str] = None
    rel_type: str = None
    target_nodeSets: List[NodeSetMeta] = None


# ToDo: Document interface functions


class CacheInterface:
    """CacheInterface
    Abstract Class to describe the interface for the cache used by neobulkmp.
    The cache in neobulkmp is used for two tasks:

    * To buffer the workloads between WorkerSourcing (The processes parsing source data) and WorkerLoading (The processes loading sourced data into the database)
    * To pass through log messages from the workers to the manager process, which handle the logs centralistic

    The implemented cache class needs to have a high perfomance backend.
    Ideas for possible cache backends:

    * Redis DB - https://redis.io/ (✓ Implemented)
    * multiprocessing.shared_memory - https://docs.python.org/3/library/multiprocessing.shared_memory.html
    * Mongo DB - https://www.mongodb.com/de
    """

    def __init__(self, cache_backend_params: Dict = None, debug: bool = False):
        self.cache_backend_params = cache_backend_params
        self.debug = debug

    def test_connection(self) -> bool:
        """Test if the cache is ready to handle orders.

        Raises:
            NotImplementedError: [description]

        Returns:
            bool: True if cache is ready to play, False if cache is not available
        """
        raise NotImplementedError

    def storage_used(self) -> int:
        """Amount of KB the cache is using.

        Returns:
            int: KB of storage available
        """
        raise NotImplementedError

    def store_is_available(self) -> bool:
        """The backend can be temporary closed by the manager. Then sourcing worker are not allowed to store nodesets.
        This can make sense if, for example, the backend memory or storage is full. And the manager first needs to assign cores to loading workers to free up memory

        Returns:
            bool: [description]
        """
        raise NotImplementedError

    def close_store(self):
        """block the storage of NodeSets and RelationshipSets see self.store_is_available for more details

        Returns:
            bool: [description]
        """
        raise NotImplementedError

    def open_store(self):
        """Open a closed to store, to let sourcing worker continue their work

        Returns:
            bool: [description]
        """
        raise NotImplementedError

    def store_NodeSet(self, set: graphio.NodeSet):
        """Store the content of a graphio.NodeSet in the cache backend. this will be done by sourcing workers.

        Args:
            set (graphio.NodeSet): [description]
        """
        raise NotImplementedError

    def store_RelSet(self, set: graphio.RelationshipSet):
        """Store the content of a graphio.RelationshipSet in the cache backend. this will be done by sourcing workers.

        Args:
            set (graphio.RelationshipSet): [description]
        """
        raise NotImplementedError

    def fetch_NodeSets(self, nodeset_meta: SetsMetaBase) -> graphio.NodeSet:
        """Return a NodeSet of a certain type from the cache. It will be removed from the cache at the same time.
        The Nodeset type will be determined by the NodeSetMeta instance. A list of all available NodeSetMeta types can be received via 'list_SetsMeta()'
        Nodesets which have to be drained (because it was ordered by CacheInterface.order_RelSetDrain()) should get the highest priority when selecting the nodes to be returned

        Args:
            nodeset_meta (SetsMetaBase): An instance of SetsMetaBase (or its child NodeSetMeta) or  which describes the NodeSet type. A list of all available SetsMetaBase types can be received via 'list_SetsMeta()'

        Returns:
            graphio.NodeSet: [description]
        """
        raise NotImplementedError

    def fetch_RelSets(
        self, relset_meta: SetsMetaBase, drain_order_id: str
    ) -> graphio.RelationshipSet:
        """Return a RelationshipSet of a certain type from the cache. It will be removed from the cache at the same time.
        The RelationshipSet type will be determined by the RelationSetMeta instance. A list of all available RelationSet types can be received via 'list_SetsMeta()'

        In contrast to fetch_NodeSets() the caller need to order a so called 'drain' before fetching RelationshipSets.
        A drain, via order_RelSetDrain() will make sure that all current NodeSets that are connected to a type of RelationShipset are flushed to the Neo4j DB.
        A drain is done when is_drain_done() says so. After a drain is done, a loading worker is allowed call fetch_RelSets() and retrieve the RelatioshipSet sets that were in the cache during the drain order

        Args:
            relset_meta (RelationSetMeta): An instance of SetsMetaBase (or its child RelationSetMeta) or  which describes the NodeSet type. A list of all available SetsMetaBase types can be received via 'list_SetsMeta()'
            drain_order_id (str): The drain order id returned by order_RelSetDrain()

        Raises:
            DrainNotReadyError: When fetch_RelSets is called before the corresponding drain of related nodeSets is ready

        Returns:
            graphio.NodeSet: [description]
        """
        raise NotImplementedError

    def list_SetsMeta(
        self, set_type: Type[Union[graphio.NodeSet, graphio.RelationshipSet]] = None
    ) -> List[SetsMetaBase]:
        """returns a list of all RelationshipSet types and all NodesetSet types that are currently in the cache.
        The first item in the list, is item with the highest priority to be loaded in the database, the second item with second highest prio..and so on.
        This can be due to the size a Node- or Relationship-Set occupies in the Cache or due to a drain order

        Args:
            set_type (Type[Union[graphio.NodeSet, graphio.RelationshipSet]], optional): [description]. Defaults to None. - Filter for NodeSets or Relationship types only

        Returns:
            List[SetsMetaBase]: List of graph sets description order by priority
        """
        raise NotImplementedError

    def get_NodeSetMeta(self, nodeset_meta: SetsMetaBase) -> NodeSetMeta:
        """Returns a more detailed description of a NodeSet (compared to SetsMetaBase), like labels and relations. NodeSetMeta is a child class of SetsMetaBase

        Args:
            nodeset_meta (SetsMetaBase): [description]

        Returns:
            NodeSetMeta: [description]
        """
        raise NotImplementedError

    def get_RelSetMeta(self, relset_meta: SetsMetaBase) -> RelationSetMeta:
        """Returns a more detailed description of a RelationSet(compared to SetsMetaBase), like end_node_labels,start_node_labels,rel_type and target nodeSets types. NodeSetMeta is a child class of SetsMetaBase

        Args:
            relset_meta (SetsMetaBase): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            RelationSetMeta: [description]
        """
        raise NotImplementedError

    def order_RelSetDrain(self, relset_meta: SetsMetaBase) -> str:
        """
        A drain order on a NodeSet insures the caller that all nodeset that are currently in the cache are empty as soon as 'CacheInterface.is_drain_done' returns True
        This is needed for the database loading workers when loading RelationSets. Workers then can be certain that all nodes that could be attached to the RelationSet are now in the DB

        Args:
            relset_meta (relset_meta): Meta data to a cached nodesets. Needed to identify drain slot. Can be obtain via 'CacheInterface.list_SetsMeta'

        Returns:
            str: drain order ticket. identifies the drain order. Needed to ask if drain order is done via 'CacheInterface.is_drain_done'
        """
        raise NotImplementedError

    def report_SetLoaded(
        self, nodeset: Union[graphio.NodeSet, graphio.RelationshipSet]
    ):
        raise NotImplementedError

    def is_drain_done(self, drain_ticket: str) -> bool:
        raise NotImplementedError

    def write_log(self, record: logging.LogRecord):
        raise NotImplementedError

    def fetch_logs(self) -> Generator[logging.LogRecord, None, None]:
        raise NotImplementedError

    def get_logs(self) -> List[logging.LogRecord]:
        raise NotImplementedError


# ToDo: Refactor RedisCache
# * evaluate to mount drain_orders to set meta data instead of workers
# * Find other opportunities to simplifiy redis cache code


class RedisCache(CacheInterface):
    NODESET_PREFIX = "NODESET:"
    RELSET_PREFIX = "RELSET:"
    DRAIN_ORDERS_KEY = "DRAIN_ORDERS_OPEN"
    DRAIN_ORDERS_READY_KEY = "DRAIN_ORDERS_READY"
    DRAIN_ORDERS_NODESETS_DONE_KEY = "DRAIN_ORDERS_NODESETS_DONE"

    # Fetch COMBINE_NODESET_COUNT amount of nodesets and combine to one for dataloading
    COMBINE_SET_COUNT = 100

    @dataclass
    class DrainOrder:
        id: str
        relset_meta: RelationSetMeta
        nodesets_meta: List[NodeSetMeta]

        buckets_key_base: str
        relset_bucket_key: str
        nodesets_buckets_keys: List[str]
        time_of_drain_order: float
        preceding_overlapping_drain_orders: List["RedisCache.DrainOrder"]

        @classmethod
        def create_order(
            cls, relset_meta: RelationSetMeta, cache: "RedisCache"
        ) -> "RedisCache.DrainOrder":
            drain_order_id = str(uuid.uuid4())
            drain_timestamp = time.time()
            buckets_key_base = f"DRAIN:{drain_order_id}:{drain_timestamp}"
            # refresh meta data
            relset_meta = cache.get_RelSetMeta(relset_meta)
            drain_order = cls(
                id=drain_order_id,
                relset_meta=relset_meta,
                nodesets_meta=relset_meta.target_nodeSets,
                buckets_key_base=buckets_key_base,
                relset_bucket_key=[],
                nodesets_buckets_keys=[],
                time_of_drain_order=drain_timestamp,
                preceding_overlapping_drain_orders=[],
            )

            return drain_order._materialize_drain_order(cache)

        @classmethod
        def get_by_order_id(
            cls, drain_order_id: uuid.UUID, cache: "RedisCache"
        ) -> "RedisCache.DrainOrder":
            p = cache.redis.pipeline()
            p.hget(cache.DRAIN_ORDERS_KEY, drain_order_id)
            p.hget(cache.DRAIN_ORDERS_READY_KEY, drain_order_id)
            results = p.execute()
            for res in results:
                if res:
                    return jsonpickle.loads(res)

        @classmethod
        def list_orders(
            cls, cache, status=None, nodeset_meta_filter: NodeSetMeta = None
        ) -> List["RedisCache.DrainOrder"]:
            p = cache.redis.pipeline()
            if status in [None, "OPEN"]:
                p.hgetall(cache.DRAIN_ORDERS_KEY)
            if status in [None, "READY"]:
                p.hgetall(cache.DRAIN_ORDERS_READY_KEY)
            results = p.execute()
            orders: List[RedisCache.DrainOrder] = []
            for res in results:
                for drain_id, raw_drain_order in res.items():
                    order: RedisCache.DrainOrder = jsonpickle.loads(raw_drain_order)
                    # If a nodeset filter is set, we search for every drain order thats affecting the nodeset in nodeset_meta_filter
                    if nodeset_meta_filter is None or (
                        nodeset_meta_filter is not None
                        and not set(nodeset_meta_filter.labels).isdisjoint(
                            set(
                                order.relset_meta.end_node_labels
                                + order.relset_meta.start_node_labels
                            )
                        )  # nodeset_meta_filter.labels in [ns.key for ns in order.nodesets_meta]
                    ):
                        orders.append(order)
            # Sort by oldest drain order first.
            return sorted(orders, key=operator.attrgetter("time_of_drain_order"))

        @classmethod
        def _list_open_nodesets_by_label(cls, cache: "RedisCache") -> List[NodeSetMeta]:
            pass

        @classmethod
        def list_open_nodesets_meta(cls, cache: "RedisCache") -> List[NodeSetMeta]:
            """Return a list of all NodeSetMeta that are affected by a drain
            Args:
                cache (RedisCache): [description]

            Returns:
                List[NodeSetMeta]: [description]
            """
            open_nodesets_meta = []

            # Get a list of all allready drained buckets keys that are part of an open drain order
            all_drained_buckets_keys = [
                bk.decode("utf-8")
                for bk in cache.redis.lrange(
                    cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, -1
                )
            ]
            # Get a list of all open drain orders
            all_open_drain_orders = cls.list_orders(cache, "OPEN")
            for drain_order in all_open_drain_orders:
                for drain_nodeset_meta, bucket_key in zip(
                    drain_order.nodesets_meta, drain_order.nodesets_buckets_keys
                ):
                    if (
                        bucket_key
                        not in all_drained_buckets_keys
                        + ["DRAIN_EMPTY_PLACEHOLDER_KEY"]
                        and drain_nodeset_meta not in open_nodesets_meta
                    ):
                        open_nodesets_meta.append(drain_nodeset_meta)
            return list(reversed(open_nodesets_meta))

        @classmethod
        def get_drain_bucket_keys(
            cls,
            cache: "RedisCache",
            graphset_meta: SetsMetaBase = None,
            set_type: Type[Union[graphio.NodeSet, graphio.RelationshipSet]] = None,
        ):
            bucket_keys = []
            all_open_drain_orders = cls.list_orders(cache, "OPEN")
            for drain_order in all_open_drain_orders:

                if set_type in [None, graphio.NodeSet]:
                    for bucket_key in drain_order.nodesets_buckets_keys:
                        if bucket_key != "DRAIN_EMPTY_PLACEHOLDER_KEY":
                            if graphset_meta is None or (
                                graphset_meta is not None
                                and graphset_meta in drain_order.nodesets_meta
                            ):
                                bucket_keys.append(bucket_key)
                if set_type in [None, graphio.RelationshipSet]:
                    if graphset_meta is None or (
                        graphset_meta is not None
                        and graphset_meta == drain_order.relset_meta
                    ):
                        bucket_keys.append(drain_order.relset_bucket_key)
            return bucket_keys

        def is_empty(self, cache):
            # if a drain order has no buckets (only "DRAIN_EMPTY_PLACEHOLDER_KEY" placeholders), it will never recieve a set_loaded message and can go stale
            all_drained_buckets_keys = [
                bk.decode("utf-8")
                for bk in cache.redis.lrange(
                    cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, -1
                )
            ]
            for bucket in self.nodesets_buckets_keys:
                if bucket != "DRAIN_EMPTY_PLACEHOLDER_KEY" and (
                    bucket not in all_drained_buckets_keys
                    or cache.redis.llen(bucket) > 0
                ):
                    return False
            for preceding_order in self.preceding_overlapping_drain_orders:
                if preceding_order.get_status(cache) == "OPEN":
                    return False
            return True

        def get_status(self, cache):
            if self.is_empty(cache):
                self._set_status(cache, "READY")
                return "READY"
            p = cache.redis.pipeline()
            p.hget(cache.DRAIN_ORDERS_KEY, self.id)
            p.hget(cache.DRAIN_ORDERS_READY_KEY, self.id)
            results = p.execute()
            if results[0]:
                return "OPEN"
            if results[1]:
                return "READY"
            return "FINISHED"

        def _set_status(self, cache: "RedisCache", status: str):
            if status == "READY":

                p = cache.redis.pipeline()
                p.multi()
                p.hdel(cache.DRAIN_ORDERS_KEY, self.id)
                p.hset(cache.DRAIN_ORDERS_READY_KEY, self.id, jsonpickle.dumps(self))
                p.execute()
            elif status == "FINISHED":
                # Delete drain order
                p = cache.redis.pipeline()
                p.multi()
                p.hdel(cache.DRAIN_ORDERS_READY_KEY, self.id)
                p.execute()
                # Delete related nodeset-done entries
                to_be_deleted_entries = []
                for key in cache.redis.lrange(
                    cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, -1
                ):
                    key = key.decode()
                    if self.id in key:
                        to_be_deleted_entries.append(key)
                for key in to_be_deleted_entries:
                    cache.redis.lrem(cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, key)

            else:
                raise ValueError(f"Expected 'READY' or 'FINISHED' got {status}")

        def get_nodeset(self, cache: "RedisCache", nodeset_meta) -> graphio.NodeSet:
            """Return nodeset from cache drain bucket

            Args:
                cache (RedisCache): [description]
                nodeset_meta ([type]): [description]

            Returns:
                graphio.NodeSet: [description]
            """

            for bucket_key, drain_nodeset_meta in zip(
                self.nodesets_buckets_keys, self.nodesets_meta
            ):
                if nodeset_meta.key == drain_nodeset_meta.key:
                    if bucket_key != "DRAIN_EMPTY_PLACEHOLDER_KEY":
                        nodeSet_parameter_dict = cache._parse_key(
                            nodeset_meta.key, cache.NODESET_PREFIX
                        )
                        ns = graphio.NodeSet.from_dict(
                            {
                                **nodeSet_parameter_dict,
                                **{
                                    "nodes": cache._fetch_list_range(
                                        bucket_key, cache.COMBINE_SET_COUNT, True
                                    )
                                },
                            }
                        )
                        ns.drain_order = self
                        ns.drain_bucket_key = bucket_key
                        ns.nodeset_meta = nodeset_meta
                        return ns
                    else:
                        return None

        def get_relset(self, cache: "RedisCache") -> graphio.RelationshipSet:
            """Return RelationshipSet from cache

            Args:
                cache (RedisCache): [description]
                nodeset_meta ([type]): [description]

            Returns:
                graphio.NodeSet: [description]
            """
            relSet_parameter_dict = cache._parse_key(
                self.relset_meta.key, cache.RELSET_PREFIX
            )
            rs = graphio.RelationshipSet.from_dict(
                {
                    **relSet_parameter_dict,
                    **{
                        "relationships": cache._fetch_list_range(
                            self.relset_bucket_key, None, True
                        )
                    },
                }
            )
            rs.drain_order = self
            rs.drain_bucket_key = self.relset_bucket_key
            rs.nodeset_meta = self.relset_meta
            return rs

        def _set_nodeset_status_drained(
            self, cache: "RedisCache", nodeset: graphio.NodeSet
        ):
            if nodeset.drain_order.id == self.id:
                # is bucket not a placeholder and is bucket not empty:
                if (
                    nodeset.drain_bucket_key != "DRAIN_EMPTY_PLACEHOLDER_KEY"
                    and cache.redis.llen(nodeset.drain_bucket_key) == 0
                ):
                    log.debug(f"SET nodeset {nodeset.labels} for {self.id} as drained")
                    cache.redis.rpush(
                        cache.DRAIN_ORDERS_NODESETS_DONE_KEY, nodeset.drain_bucket_key
                    )
                    return True
                else:
                    # Bucket is not empty. we wont set status to drained
                    return False
            else:
                raise ValueError(
                    f"NodeSet '{':'.join(nodeset.labels)}' is not target of DrainOrder:id'{self.id}'"
                )

        def are_nodesets_drained(self, cache: "RedisCache"):
            # Check preceding overlapping drain orders
            for other_drain_orders in self.preceding_overlapping_drain_orders:
                if not other_drain_orders.are_nodesets_drained(cache):
                    return False
            # Check self

            # check first if drain order is still existent
            if self.get_status(cache) == "FINISHED":
                return True

            # Get a list a fullfilled drained nodeset buckets
            all_drained_buckets_keys = [
                bucketkey.decode("utf-8")
                for bucketkey in cache.redis.lrange(
                    cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, -1
                )
            ]

            # get own drain order buckets
            self_bucket_keys = [
                bucketkey
                for bucketkey in self.nodesets_buckets_keys
                if bucketkey != "DRAIN_EMPTY_PLACEHOLDER_KEY"
            ]
            # check if all own buckets appear in fullfilled bucket list
            if set(self_bucket_keys).issubset(set(all_drained_buckets_keys)):
                return True
            else:
                return False

        @classmethod
        def set_graphset_drained(
            cls,
            cache: "RedisCache",
            graphset: Union[graphio.NodeSet, graphio.RelationshipSet],
        ):
            if isinstance(graphset, graphio.NodeSet):
                if cache.debug:
                    all_drained_buckets_keys = [
                        bucketkey.decode("utf-8")
                        for bucketkey in cache.redis.lrange(
                            cache.DRAIN_ORDERS_NODESETS_DONE_KEY, 0, -1
                        )
                    ]
                    if graphset.drain_bucket_key in all_drained_buckets_keys:
                        raise ValueError(
                            f"Graphset({len(graphset.nodes)} nodes) '{graphset.drain_bucket_key}' is allready set as drained. It was called a second time :("
                        )

                graphset.drain_order._set_nodeset_status_drained(cache, graphset)
                if graphset.drain_order.are_nodesets_drained(cache):
                    log.info(
                        f"Drain order for '{graphset.drain_order.relset_meta.rel_type}' is ready. RelationSet can be loaded now"
                    )
                    graphset.drain_order._set_status(cache, "READY")
            elif isinstance(graphset, graphio.RelationshipSet):
                log.info(f"Drain order for '{graphset.rel_type}' is finished")
                graphset.drain_order._set_status(cache, "FINISHED")

        def set_drain_order_done(self, cache):
            p = cache.redis.pipeline()
            p.hdel(cache.DRAIN_ORDERS_KEY, self.id)
            p.lpush("DRAINS_DONE", self.id)
            p.execute()

        def _materialize_drain_order(self, cache):
            """
            To actually create the drain order we need to
                * seperate the relSet all affected nodesets each to a "drain bucket"
                * get all other current drain orders to later check if there are overlapping drain orders (relationshipSets that are targeting at the same nodeset)
                * make an entry in the redis drain order list to proclaim the drain order (for other processes to interact with the drain oder)
            """
            # Get other drain orders, to check overlaps
            other_drain_orders = cache.redis.hgetall(cache.DRAIN_ORDERS_KEY)

            # Check other drain order for overlap and update drain order if there are other drainorders
            overlapping_drain_orders = []
            for drain_id, pickled_drain_order in other_drain_orders.items():
                other_drain_order: RedisCache.DrainOrder = jsonpickle.loads(
                    pickled_drain_order
                )
                # if other drain order shares one or two nodesets its overlapping
                if [
                    other_ns
                    for other_ns in other_drain_order.nodesets_meta
                    if other_ns in self.nodesets_meta
                ]:
                    overlapping_drain_orders.append(other_drain_order)

            if overlapping_drain_orders:
                # update drain order if there were overlaping other drain orders
                self.preceding_overlapping_drain_orders = overlapping_drain_orders

            # Move nodesets to drain buckets
            self.nodesets_buckets_keys = []
            for set_meta in self.nodesets_meta:
                drain_key = f"{self.buckets_key_base}:{set_meta.key}"
                # Move current content of set to a new location
                try:
                    cache.redis.rename(set_meta.key, drain_key)
                except redis.exceptions.ResponseError:
                    # To be drained nodeset was empty not existent.
                    # atm we can not rename it.
                    # this happens when a beforehand worker just ordered a drain or the nodeset was coincidentally just loaded
                    # We will just provide a placeholder key
                    drain_key = "DRAIN_EMPTY_PLACEHOLDER_KEY"
                self.nodesets_buckets_keys.append(drain_key)
            # generate drain bucket for relatioshipset
            self.relset_bucket_key = f"{self.buckets_key_base}:{self.relset_meta.key}"
            # move relationset to drain bucket
            try:
                cache.redis.rename(self.relset_meta.key, self.relset_bucket_key)
            except redis.exceptions.ResponseError:
                log.error(
                    f"Failed renaming {self.relset_meta.key} to {self.relset_bucket_key}"
                )
                raise
            # proclaim the drain order: Save the meta data of the drain a key value pair a redis hashlist called cache.DRAIN_ORDERS_KEY

            cache.redis.hmset(cache.DRAIN_ORDERS_KEY, {self.id: jsonpickle.dumps(self)})

            # Check if nodesets are empty and drain is allready fullfilled
            if self.are_nodesets_drained(cache):
                self._set_status(cache, "READY")
            return self

    def __init__(self, cache_backend_params: Dict = None, debug: bool = False):
        super(type(self), self).__init__()
        if cache_backend_params is None:
            cache_backend_params = {"host": "localhost"}
        self.redis = redis.Redis(**cache_backend_params)

    def test_connection(self) -> bool:
        res = self.redis.info()
        if res:
            return True
        else:
            return False

    def storage_used(self) -> int:
        return self.redis.execute_command("INFO")["used_memory_rss"]

    def store_is_available(self) -> bool:
        if self.redis.get("STORE_STATUS"):
            # Store is closed by manager
            return False
        else:
            return True

    def close_store(self) -> bool:
        """block the storage of NodeSets and RelationshipSets see self.store_is_available for more details

        Returns:
            bool: [description]
        """
        self.redis.set("STORE_STATUS", "CLOSED")

    def open_store(self) -> bool:
        """Open a closed to store, to let sourcing worker continue their work

        Returns:
            bool: [description]
        """
        self.redis.delete("STORE_STATUS")

    def store_NodeSet(self, set: graphio.NodeSet):
        set_dict = set.to_dict()
        data = set_dict.pop("nodes", [])
        cache_key = self.NODESET_PREFIX + json.dumps(set_dict)
        self.redis.lpush(cache_key, json.dumps(data))
        log.debug(f"store_NodeSet '{cache_key}'")
        # self.redis.lpush(cache_key, json.dumps(data))

    def store_RelSet(self, set: graphio.RelationshipSet):
        data = {}
        set_dict = set.to_dict()
        data = set_dict.pop("relationships", [])
        cache_key = self.RELSET_PREFIX + json.dumps(set_dict)
        self.redis.lpush(cache_key, json.dumps(data))
        log.debug(f"store_RelSet '{cache_key}'")

    def _fetch_list_range(
        self, key: str, range_size: int = None, parse_and_combine=True
    ) -> List:
        # fetch and delete from cache in one transaction
        p = self.redis.pipeline()
        # watch key for change
        # p.watch(key)
        # starts transactional block of pipeline
        p.multi()

        if range_size is None:
            # get all nodesets
            p.lrange(key, 0, -1)
            # delete key
            p.delete(key)
        else:
            # get first 'range_size' nodesets
            p.lrange(key, 0, range_size - 1)
            # delete first 'range_size' nodesets
            p.ltrim(key, range_size, -1)

        # ends transactional block of pipeline
        result = p.execute()
        if parse_and_combine:
            return [item for sublist in result[0] for item in json.loads(sublist)]
        else:
            return result[0]

    def _parse_key(self, key: str, prefix: str) -> Dict:
        key_data = None
        if isinstance(key, bytes):
            key_str = key.decode()
        else:
            key_str = key

        if key_str.startswith(prefix):
            key_data = json.loads(key[len(prefix) :])
        else:
            raise ValueError(
                f"Wrong key type. Expected '{prefix}{{somekeydata}}. Got {key}"
            )
        return key_data

    def fetch_NodeSets(self, nodeset_meta: NodeSetMeta) -> graphio.NodeSet:
        # Decode keydata for creating ndoeset
        # example keydata: 'NODESET:{"labels": ["Movie"], "merge_keys": "title"}'

        # Check if there are any open drainOrders on this type of NodeSet
        # If yes we return the oldest/first drain bucket of this nodeset
        if isinstance(nodeset_meta, SetsMetaBase):
            nodeset_meta = self.get_NodeSetMeta(nodeset_meta)
        drain_orders = RedisCache.DrainOrder.list_orders(
            self, status="OPEN", nodeset_meta_filter=nodeset_meta
        )
        if drain_orders:
            ns = drain_orders[0].get_nodeset(self, nodeset_meta=nodeset_meta)
            if ns:
                return ns

        # there are not drain orders, we can return content from the general bucket
        nodeSet_parameter_dict = self._parse_key(nodeset_meta.key, self.NODESET_PREFIX)
        # Fetch data from cache, combine result of different workers to one large nodeset and create a graphio.NodeSet based on that data
        return graphio.NodeSet.from_dict(
            {
                **nodeSet_parameter_dict,
                **{
                    "nodes": self._fetch_list_range(
                        nodeset_meta.key, self.COMBINE_SET_COUNT, True
                    )
                },
            }
        )

    def fetch_RelSets(
        self, relset_meta: SetsMetaBase, drain_order_id: str
    ) -> graphio.RelationshipSet:
        # Decode key data
        # example key: "RELSET:{\"rel_type\": \"ACTS_IN\", \"start_node_labels\": [\"Actor\"], \"end_node_labels\": [\"Movie\"], \"start_node_properties\": [\"name\"], \"end_node_properties\": [\"title\"], \"unique\": false}"
        drain_order = RedisCache.DrainOrder.get_by_order_id(drain_order_id, self)
        if self.debug and not drain_order.are_nodesets_drained(self):
            log.exception(
                f"Drain not finished, but relationship was tried to fetch. drain order id {drain_order_id}"
            )
            raise DrainNotReadyError

        relset_meta_dict = self._parse_key(relset_meta.key, self.RELSET_PREFIX)
        # Fetch relatipshipSet from bucket
        return drain_order.get_relset(self)

    def list_SetsMeta(
        self, set_type: Type[Union[graphio.NodeSet, graphio.RelationshipSet]] = None
    ) -> List[SetsMetaBase]:
        meta_data = []
        if set_type in [None, graphio.NodeSet]:
            # fetch all keys begining with NODESET_PREFIX and pack each into an SetsMetaBase instance
            set_keys = {
                key.decode("utf-8")
                for key in self.redis.keys(f"{self.NODESET_PREFIX}*")
            }
            """drain_nodeset_keys = {
                key.decode("utf-8").split(":", 3)[3]
                for key in self.redis.keys(f"DRAIN:*:{self.NODESET_PREFIX}*")
            }
            nodeset_keys = nodeset_keys | drain_nodeset_keys
            log.info(f"nodeset_keys: {nodeset_keys}")"""
            for nkey in set_keys:
                meta_entry = SetsMetaBase(
                    key=nkey, total_size_bytes=0, type=graphio.NodeSet
                )
                meta_entry.total_size_bytes = self._get_NodeSet_real_size(meta_entry)
                meta_data.append(meta_entry)

        if set_type in [None, graphio.RelationshipSet]:
            # fetch all keys begining with RELSET_PREFIX and pack each into an SetsMetaBase instance
            set_keys = [
                key.decode("utf-8") for key in self.redis.keys(f"{self.RELSET_PREFIX}*")
            ]
            meta_data = []
            for key in set_keys:
                # TODO: maybe it would make sense here to add related NodeSet size into total_size_bytes? this would prioritize larger nodesets to be drained first. does this make sense? think about it!
                meta_entry = SetsMetaBase(
                    key=key,
                    total_size_bytes=self.redis.memory_usage(key),
                    type=graphio.RelationshipSet,
                )
                meta_data.append(meta_entry)
        # Sort by priority (Drainorders first, then by size)
        meta_data.sort(key=operator.attrgetter("total_size_bytes"), reverse=True)

        if set_type in [None, graphio.NodeSet]:
            # Move nodesets with drain order to the front
            for open_drain_nodeset_meta in list(
                reversed(RedisCache.DrainOrder.list_open_nodesets_meta(cache=self))
            ):
                # check if nodeset appears in list of nodeset with a drainOrder, if yes get index this nodeset in meta_data list
                index = next(
                    (
                        i
                        for i, md in enumerate(meta_data)
                        if md.key in open_drain_nodeset_meta.key
                    ),
                    None,
                )
                if index not in [None, 0]:
                    # if nodeset_meta appeard in a drain order move it to the front
                    # pop it first into tmp var...
                    md = meta_data.pop(index)
                elif index is None:
                    # if drain order references a nodeset that was not fetched into 'meta_data'
                    # this can happen when a drain order justed moved the whole nodeset content to a drain bucket and no new nodeset were supplied by sourcing workers
                    md = open_drain_nodeset_meta
                    md.total_size_bytes = self._get_NodeSet_real_size(md)
                if index != 0:
                    # ... insert it to the front of the list
                    meta_data.insert(0, md)

        return meta_data

    def get_NodeSetMeta(self, nodeset_meta: SetsMetaBase) -> NodeSetMeta:
        node_meta = NodeSetMeta(
            key=nodeset_meta.key,
            total_size_bytes=nodeset_meta.total_size_bytes,  # self._get_NodeSet_real_size(nodeset_meta) # refresh ob total size is not used/needed so far. we can shave that off
        )
        node_meta.labels = self._parse_key(nodeset_meta.key, self.NODESET_PREFIX)[
            "labels"
        ]
        # unused. TODO: to be removed:
        """node_meta.relations = []
        all_rel_sets = self.list_SetsMeta(set_type=graphio.RelationshipSet)
        for rel in all_rel_sets:
            rel_data = self._parse_key(rel.key, self.RELSET_PREFIX)
            if set(node_meta.labels) in [
                set(rel_data["start_node_labels"]),
                set(rel_data["end_node_labels"]),
            ]:
                node_meta.relations.append(rel)"""
        # unused-end
        return node_meta

    def _get_NodeSet_real_size(self, nodeSet_meta: SetsMetaBase) -> int:
        # NodeSets of one key can be distributed in many drain buckets
        # to get the real site of a nodeset in chache we need to add alle these buckets together with the origin list

        bucket_keys = RedisCache.DrainOrder.get_drain_bucket_keys(
            cache=self, graphset_meta=nodeSet_meta, set_type=graphio.NodeSet
        )
        size = 0
        for bucket_key in bucket_keys + [nodeSet_meta.key]:
            dsize = self.redis.memory_usage(bucket_key)
            if dsize:
                size += dsize
        return size

    def get_RelSetMeta(self, relset_meta: SetsMetaBase) -> RelationSetMeta:
        rel_meta = RelationSetMeta(
            key=relset_meta.key,
            total_size_bytes=self.redis.memory_usage(relset_meta.key),
        )
        rel_key_data = self._parse_key(rel_meta.key, self.RELSET_PREFIX)
        rel_meta.rel_type = rel_key_data["rel_type"]
        rel_meta.start_node_labels = rel_key_data["start_node_labels"]
        rel_meta.end_node_labels = rel_key_data["end_node_labels"]
        rel_meta.target_nodeSets = []
        all_node_sets = self.list_SetsMeta(set_type=graphio.NodeSet)
        for nodeset in all_node_sets:
            nodeset_data = self._parse_key(nodeset.key, self.NODESET_PREFIX)
            if set(nodeset_data["labels"]) in [
                set(rel_key_data["start_node_labels"]),
                set(rel_key_data["end_node_labels"]),
            ]:
                rel_meta.target_nodeSets.append(nodeset)
        return rel_meta

    def order_RelSetDrain(self, relset_meta: SetsMetaBase) -> str:

        drain_order: self.DrainOrder = self.DrainOrder.create_order(relset_meta, self)
        log.info(f"Order Drain for {drain_order.relset_meta.rel_type}")
        return drain_order.id

    def is_drain_done(self, drain_order: Union["RedisCache.DrainOrder", str]) -> bool:
        d_order = None
        if isinstance(drain_order, str):
            d_order = RedisCache.DrainOrder.get_by_order_id(drain_order, self)
        elif isinstance(drain_order, RedisCache.DrainOrder):
            d_order = drain_order
        else:
            raise ValueError(
                f"Expected 'RedisCache.DrainOrder' or 'str', got {type(drain_order)}"
            )
        if d_order.get_status(self) in ["READY"]:
            return True
        else:
            return False

    def report_SetLoaded(
        self, graphset: Union[graphio.NodeSet, graphio.RelationshipSet]
    ):
        if hasattr(graphset, "drain_order"):
            RedisCache.DrainOrder.set_graphset_drained(self, graphset)

    def write_log(self, record: logging.LogRecord):
        # self.redis.lpush("LOGSTEST", jsonpickle.dumps(record))
        try:
            self.redis.rpush("LOG_LIST", jsonpickle.dumps(record))
            # pusblish seems to be broken; see fetch_logs() comments.
            # self.redis.publish("LOG_LIST", jsonpickle.dumps(record)))
        except:
            print(traceback.format_exc())
            self.redis.rpush("LOG_LIST", traceback.format_exc())
            raise

    def fetch_logs(self) -> Generator[logging.LogRecord, None, None]:
        """redis-py pub/sub is broken somehow. always only returns '1' (as int) as data

        pub = self.redis.pubsub()
        pub.subscribe("LOG_STREAM")
        for raw_record in pub.listen():
            yield jsonpickle.loads(raw_record)
        """

        # for now we will use a plain redis list as a queue for the time being (instead of the broken pub/sub system).
        # in a later iteration i would like to switch from redis-py to aioredis and give the pubsub system another try
        while True:
            record = self.redis.blpop("LOG_LIST", timeout=1)
            if record and "LOG_LIST" in record and record["LOG_LIST"]:
                yield jsonpickle.loads(record["LOG_LIST"])
            # time.sleep(0.005)

    def get_logs(self) -> List[logging.LogRecord]:
        return [
            jsonpickle.loads(record) for record in self.redis.lrange("LOG_LIST", 0, -1)
        ]
