from __future__ import annotations

from pyathena.util import synchronized

import karnak.util.log as kl
import karnak.util.aws.sqs as ksqs

from abc import abstractmethod
from typing import Dict, List, Optional, Union, Type
import datetime
import time
import pandas as pd
import json
import threading
import copy


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# TODO: convert to immutable
class KarnakFetcherQueueItem:
    def __init__(self, key: str,
                 key_property: str,
                 table: str,
                 extractor: str,
                 current_retries: int = 0,
                 created_at: Optional[datetime.datetime] = None,
                 updated_at: Optional[datetime.datetime] = None,
                 cohort: Optional[str] = None,
                 priority: Optional[int] = None,
                 fetch_errors: Optional[List[str]] = None,
                 handle: str = None):
        now = datetime.datetime.now()
        self.key: str = key
        self.key_property: str = key_property
        self.table: str = table
        self.extractor: str = extractor
        self.created_at: datetime.datetime = created_at if created_at is not None else now
        self.updated_at: datetime.datetime = updated_at if updated_at is not None else now
        self.cohort: Optional[str] = cohort
        self.priority: Optional[int] = priority
        self.current_retries: int = current_retries
        self.fetch_errors: Optional[List[str]] = fetch_errors if fetch_errors is not None else []
        self.handle: str = handle

    def copy(self) -> KarnakFetcherQueueItem:
        return copy.copy(self)

    def restart(self, extractor: str = None) -> KarnakFetcherQueueItem:
        _extractor = self.extractor if extractor is None else extractor
        return KarnakFetcherQueueItem(key=self.key,
                                      key_property=self.key_property,
                                      table=self.table,
                                      extractor=_extractor,
                                      created_at=self.created_at,
                                      cohort=self.cohort,
                                      priority=self.priority)

    def set_priority(self, priority) -> KarnakFetcherQueueItem:
        c = self.copy()
        if priority is not None:
            c.priority = priority
        return c

    def set_extractor(self, extractor, reset_errors=False) -> KarnakFetcherQueueItem:
        c = self.copy()
        if extractor is not None:
            c.extractor = extractor
        if reset_errors:
            c.current_retries = 0
            c.fetch_errors = []
        return c

    def to_string(self):
        filtered_dict = self.__dict__.copy()
        del filtered_dict['handle']
        js = json.dumps(filtered_dict, default=json_serial)
        return js

    @classmethod
    def from_string(cls, string, handle=None):
        d = json.loads(string)
        try:
            f = KarnakFetcherQueueItem(key=d.get('key'),
                                       key_property=d.get('key_property'),
                                       table=d.get('table'),
                                       extractor=d.get('extractor'),
                                       created_at=datetime.datetime.fromisoformat(d.get('created_at')),
                                       updated_at=datetime.datetime.fromisoformat(d.get('updated_at')),
                                       cohort=d.get('cohort'),
                                       priority=d.get('priority'),
                                       current_retries=d.get('current_retries'),
                                       fetch_errors=d.get('fetch_errors'),
                                       handle=handle)
        except KeyError:
            msg = string.replace("\n", "")
            kl.error(f'invalid message: {msg}')
            return None
        return f


class KarnakFetcherResult:
    def __init__(self, queue_item: KarnakFetcherQueueItem,
                 result: Union[None, dict, str],
                 elapsed: datetime.datetime,
                 is_success: bool = True,
                 can_retry: bool = False,
                 compression: str = None,
                 error_type: str = None,
                 error_message: str = None,
                 handle: str = None):
        self.queue_item = queue_item
        self.result = result
        self.elapsed = elapsed
        self.is_success = is_success,
        self.can_retry = can_retry,
        self.compression = compression,
        self.error_type = error_type
        self.error_message = error_message
        self.handle = handle

    def elapsed_str(self):
        return str(self.elapsed)

    def to_string(self):
        filtered_dict = self.__dict__.copy()
        del filtered_dict['handle']
        js = json.dumps(filtered_dict, default=json_serial)
        return js

    @classmethod
    def from_string(cls, s: str, handle=None):
        d = json.loads(s)
        qi = KarnakFetcherQueueItem.from_string(s)
        if qi is None:
            return None
        try:

            fr = KarnakFetcherResult(queue_item=qi,
                                     result=d.get('result'),
                                     elapsed=d.get('elapsed'),
                                     is_success=d.get('is_success'),
                                     can_retry=d.get('can_retry'),
                                     compression=d.get('compression'),
                                     error_type=d.get('error_type'),
                                     error_message=d.get('error_message'),
                                     handle=handle)
            return fr
        except KeyError:
            msg = s.replace("\n", " ")
            kl.error(f'invalid message: {msg}')
            return None


class KarnakFetcherThreadContext:
    pass


class KarnakSqsFetcherThreadContext(KarnakFetcherThreadContext):
    def __init__(self):
        self.sqs_client = ksqs.get_client()


class KarnakFetcher:
    def __init__(self, name: str,
                 tables: List[str],
                 environment: str,
                 extractors: Optional[List[str]] = None,
                 max_priority: Optional[int] = None):
        self.name: str = name
        self.tables: List[str] = tables
        self.environment: str = environment
        self.extractors: Optional[List[str]] = extractors if extractors is not None else ['default']
        self.max_priority: Optional[int] = max_priority

    #
    # general
    #

    def priorities(self) -> List[Optional[int]]:
        return [None] if self.max_priority is None else list(range(1, self.max_priority + 1)) + [None]

    @abstractmethod
    def fetcher_state(self, queue_sizes: Optional[Dict[str, int]] = None) -> (str, int):
        """
        Returns de state of the fetcher
        ;param queue_sizes: dict with precalculated (queue name, queue size)
        :return: (str) one of the values: 'idle' (all worker queues empty), 'working' (worker queues with data),
                'consolidating' (only results queue not empty)
                (int) smallest priority of queue with pending items
        """
        pass

    #
    # kickoff
    #

    @abstractmethod
    def keys_to_fetch(self, table: str,
                      max_keys: Optional[int] = None,
                      add_keys: Optional[List[str]] = None,
                      method: Optional[str] = None,
                      scope: Optional[str] = None,
                      **args) -> List[KarnakFetcherQueueItem]:
        """
        Returl list of keys to fetch
        :param table: table to fetch
        :param max_keys: max number of keys to fetch
        :param add_keys: add this keys to fetch
        :param method: method to find keys to fetch
        :param scope: scope to limit keys fetched
        :param args: additional arguments needed for derived classes
        :return: list of items to be fetched
        """
        return []

    def kickoff_ready(self, empty_priority:  Optional[int] = None) -> (bool, str):
        state, working_priority = self.fetcher_state()
        if state != 'working':
            return True, state
        elif empty_priority is None:
            return False, state
        else:
            return (working_priority > empty_priority), state

    def set_initial_extractor(self, items: List[KarnakFetcherQueueItem]):
        return items

    @abstractmethod
    def populate_worker_queue(self, items: List[KarnakFetcherQueueItem], extractor: str, priority: Optional[int]):
        pass

    def kickoff(self, table: str,
                max_keys: Optional[int] = None,
                add_keys: Optional[List[str]] = None,
                method: Optional[str] = None,
                scope: Optional[str] = None,
                priority: Optional[int] = None,
                if_empty: bool = False,
                wait_empty: bool = False,
                empty_priority: Optional[int] = None,
                extractors: List[str] = None,
                **args) -> bool:

        _extractors = extractors if extractors is not None else self.extractors

        # test if its ready to kickoff
        if if_empty:
            kickoff_ready, state = self.kickoff_ready(empty_priority)
            if not kickoff_ready:
                kl.info(f'cannot kickoff {self.name} table {table}: current state is {state}.')
                return False
        elif wait_empty:
            wait_time_seconds = 60
            while True:
                kickoff_ready, state = self.kickoff_ready(empty_priority)
                if kickoff_ready:
                    break
                kl.info(f'waiting {wait_time_seconds}s for kickoff {self.name} table {table}:'
                        f' current state is {state}.')
                time.sleep(wait_time_seconds)

        # keys and initial strategies
        items = self.keys_to_fetch(table=table, max_keys=max_keys, add_keys=add_keys,
                                   method=method, scope=scope, **args)

        if items is None or len(items) == 0:
            kl.info(f'cannot kickoff {self.name} table {table}: nothing to fetch.')
            return False

        # set priority, cohort, creation time
        if priority is not None:
            items = [x.set_priority(priority) for x in items]

        # set initial extractor
        if len(self.extractors) > 0:
            items = self.set_initial_extractor(items)

        for extractor in _extractors:
            extractor_items = [x for x in items if x.extractor == extractor]
            kl.debug(f'populating extractor {extractor} with {len(extractor_items)} items.')
            self.populate_worker_queue(extractor_items, extractor=extractor, priority=priority)

        kl.debug(f'kickoff completed for {self.name} table {table}.')

    #
    # worker
    #

    @abstractmethod
    def pop_work_queue_item(self, extractor: str, priority: Optional[int],
                            context: KarnakFetcherThreadContext,
                            wait_seconds: int) \
            -> Optional[KarnakFetcherQueueItem]:
        pass

    @abstractmethod
    def pop_best_work_queue_item(self, extractor: str,
                                 context: KarnakFetcherThreadContext,
                                 wait_seconds: int = 30) -> Optional[KarnakFetcherQueueItem]:
        pass

    #
    # consolidator
    #

    @abstractmethod
    def pop_result_items(self, max_items) -> List[KarnakFetcherResult]:
        pass

    @abstractmethod
    def consolidate(self, max_queue_items_per_file: int, max_rows_per_file: int, **args):
        pass


class KarnakSqsFetcher(KarnakFetcher):
    def __init(self, name: str,
               tables: List[str],
               environment: str,
               extractors: Optional[List[str]] = None,
               max_priority: Optional[int] = None,
               empty_work_queue_recheck_seconds: int = 60):
        super().__init__(name, tables, environment, extractors, max_priority)
        self.empty_queue_control = {}
        self.default_sqs_client = ksqs.get_client()
        self.empty_work_queue_recheck_seconds = empty_work_queue_recheck_seconds

    #
    # queues
    #

    @abstractmethod
    def results_queue_name(self) -> str:
        """Returns the name of the results queue."""
        pass

    @abstractmethod
    def worker_queue_name(self, extractor: str, priority: Optional[int]) -> str:
        """Returns the name of the worker queue."""
        pass

    def worker_queue_names(self, extractor=None) -> List[str]:
        priorities = self.priorities()
        _extractors = [extractor] if extractor is not None else self.extractors
        ql = [self.worker_queue_name(ext, p) for ext in _extractors for p in priorities]
        return ql

    def fetcher_state(self, queue_sizes: Optional[Dict[str, int]] = None) -> (str, int):
        if queue_sizes is None:
            queue_sizes = self.queue_sizes()
        qs_results = queue_sizes[self.results_queue_name()]
        qs_workers = sum([queue_sizes[qn] for qn in self.worker_queue_names()])
        working_priority = None
        if self.max_priority is not None and qs_workers > 0:
            for p in range(1, self.max_priority + 1):
                q_names = [self.worker_queue_name(ext, p) for ext in self.extractors]
                cnt = sum([queue_sizes[qn] for qn in q_names])
                if cnt > 0:
                    working_priority = p
                    break

        if qs_results + qs_workers == 0:
            return 'idle', working_priority
        elif qs_workers == 0:
            return 'consolidating', working_priority
        else:
            return 'working', working_priority

    def queue_sizes(self, sqs_client=None) -> Dict[str, int]:
        """Returns approximate message count for all queues."""
        kl.trace(f'getting queue sizes')
        _sqs_client = sqs_client if sqs_client is not None else self.default_sqs_client
        qs = {}
        queue_names = self.worker_queue_names() + [self.results_queue_name()]
        for q in queue_names:
            attr = ksqs.queue_attributes(q, sqs_client=_sqs_client)
            available = int(attr['ApproximateNumberOfMessages'])
            in_flight = int(attr['ApproximateNumberOfMessagesNotVisible'])
            delayed = int(attr['ApproximateNumberOfMessagesDelayed'])
            qs[q] = available + in_flight + delayed
        return qs

    #
    # kickoff
    #

    def populate_worker_queue(self, items: List[KarnakFetcherQueueItem], extractor: str, priority: Optional[int]):
        contents = [i.to_string() for i in items]
        ksqs.send_messages(self.worker_queue_name(extractor=extractor, priority=priority), contents)

    #
    # worker
    #

    def create_thread_context(self) -> KarnakSqsFetcherThreadContext:
        ctx = KarnakSqsFetcherThreadContext()
        return ctx

    @synchronized
    def set_empty_queue(self, queue_name):
        self.empty_queue_control[queue_name] = datetime.datetime.now()

    @synchronized
    def is_empty_queue(self, queue_name) -> bool:
        eqc = self.empty_queue_control.get(queue_name)
        if eqc is None:
            return True
        now = datetime.datetime.now()
        if now - eqc >= datetime.timedelta(seconds=self.empty_work_queue_recheck_seconds):
            del self.empty_queue_control[queue_name]
            return True
        return False

    def pop_work_queue_item(self, extractor: str, priority: Optional[int],
                            context: KarnakSqsFetcherThreadContext,
                            wait_seconds: int) \
            -> Optional[KarnakFetcherQueueItem]:
        queue_name = self.worker_queue_name(extractor, priority=priority)
        sqs_client = context.sqs_client
        items = ksqs.receive_messages(queue_name=queue_name, max_messages=1, wait_seconds=wait_seconds,
                                      sqs_client=sqs_client)
        if items is None or len(items) == 0:
            self.set_empty_queue(queue_name)
            return None
        else:
            assert len(items) == 1
            handle = list(items.keys())[0]
            content_str = items[handle]
            ret = KarnakFetcherQueueItem.from_string(content_str, handle=handle)
            return ret

    def pop_best_work_queue_item(self, extractor: str,
                                 context: KarnakSqsFetcherThreadContext,
                                 wait_seconds: int = 30) -> Optional[KarnakFetcherQueueItem]:
        priorities = self.priorities()
        for retry in [0, 1]:  # two rounds of attempts
            for p in priorities:
                queue_name = self.worker_queue_name(extractor, priority=p)
                if retry or not self.is_empty_queue(queue_name, wait_seconds):
                    # only wait in retry round
                    _wait_seconds = wait_seconds if retry else 0
                    item = self.pop_work_queue_item(extractor, p, context, _wait_seconds)
                    if item is not None:
                        return item

    #
    # consolidator
    #

    def pop_result_items(self, max_items)  -> List[KarnakFetcherResult]:
        items = ksqs.receive_messages(queue_name=self.results_queue_name(),
                                      max_messages=max_items)
        ret = [KarnakFetcherResult.from_string(items[handle], handle=handle) for handle in items if items is not None]
        return ret

    def consolidate(self, max_queue_items: int = 120_000, max_rows_per_file: int = 2_000_000, **args):
        kl.debug(f'consolidate {self.name}: start.')

        qs = self.queue_sizes()
        qs_results = qs[self.results_queue_name()]
        state = self.fetcher_state(qs)
        if qs_results == 0:
            kl.info(f'consolidate {self.name}: nothing to consolidate. State: {state}')
            return

        # get all messages from result queue
        remaining = qs_results
        while remaining > 0:
            messages_to_fetch = min(remaining, 120_000, max_queue_items)
            kl.debug(f'reading {messages_to_fetch} messages from results queue...')
            results: List[KarnakFetcherResult] = []
            while len(results) < messages_to_fetch:
                next_to_fetch = messages_to_fetch - len(results)
                new_results = self.pop_result_items(max_items=next_to_fetch)
                kl.debug(f'read {len(new_results)} new messages.')
                results.extend(new_results)
                if len(new_results) == 0:
                    break
            if len(results) == 0:
                break
            remaining -= len(results)
            fetched_data = [i.result for i in results]
            fetched_df = self.data_to_df(fetched_data)

            self.save_consolidated(fetched_df, **args)
            del fetched_df

            handles = [i.handle for i in results]
            ksqs.remove_messages(queue_name=self.results_queue_name(), receipt_handles=handles)
            del fetched_data

        kl.debug(f'consolidate {self.name}: finish.')

    @abstractmethod
    def save_consolidated(self, fetched_df: pd.DataFrame, **args):
        pass

    def data_to_df(self, fetched_data: list) -> pd.DataFrame:
        return pd.DataFrame(fetched_data)


class KarnakFetcherWorker:
    def __init__(self, fetcher: KarnakFetcher, extractor: str, n_threads: int = 1,
                 loop_pause_seconds: int = 180, queue_wait_seconds = 30):
        self.fetcher: KarnakFetcher = fetcher
        self.extractor = extractor
        # self.worker_queue_name = self.fetcher.worker_queue(self.strategy)
        # self.items_per_request = items_per_request
        self.n_threads = n_threads
        self.loop_pause_seconds = loop_pause_seconds
        self.queue_wait_seconds = queue_wait_seconds

        self.state = 'working'
        # self.state_check_lock = threading.RLock()

    def throttle_request(self):
        pass

    @abstractmethod
    def pop_work_queue_item(self, priority: Optional[int],
                            context: KarnakFetcherThreadContext,
                            wait_seconds: int) -> Optional[KarnakFetcherQueueItem]:
        pass

    @abstractmethod
    def pop_best_work_queue_item(self,
                                 context: KarnakFetcherThreadContext,
                                 wait_seconds: int = 30) -> Optional[KarnakFetcherQueueItem]:
        pass

    @abstractmethod
    def return_queue_item(self, item: KarnakFetcherQueueItem, context: KarnakFetcherThreadContext):
        pass

    @abstractmethod
    def push_queue_item(self, item: KarnakFetcherQueueItem, context: KarnakFetcherThreadContext):
        pass

    @abstractmethod
    def refresh_queue_item(self, item: KarnakFetcherQueueItem,
                           context: KarnakFetcherThreadContext,
                           new_extractor: str = None,
                           new_priority: int = None):
        pass

    @abstractmethod
    def complete_queue_item(self, item: KarnakFetcherResult, context: KarnakFetcherThreadContext):
        pass

    @abstractmethod
    def fetch_item(self, item: KarnakFetcherQueueItem, context: KarnakFetcherThreadContext) -> KarnakFetcherResult:
        pass

    @abstractmethod
    def decide_failure_action(self, item: KarnakFetcherResult) -> (str, str):
        """Return:
                ('abort', None): do not try again.
                ('ignore', None): return message to queue.
                ('retry', None): retry in same strategy.
                ('retry', 'xpto'): move to strategy xpto.
                ('restart', 'xpto'): save in current strategy, and also reset errors and create new task in new strategy
        """
        return 'abort', None

    @classmethod
    def new_thread_context(cls) -> KarnakFetcherThreadContext:
        ctx = KarnakFetcherThreadContext()
        return ctx

    def process_item(self, item: KarnakFetcherQueueItem, thread_context: KarnakFetcherThreadContext):
        result = self.fetch_item(item, thread_context)

        if result.is_success:
            # successful ones: move to results
            kl.debug(f"success fetching {result.queue_item.key} in {result.elapsed_str()}, "
                     f"attempt {result.queue_item.current_retries}")
            self.complete_queue_item(result, thread_context)
        else:  # failure
            action, new_extractor = self.decide_failure_action(result)
            if action == 'abort':
                self.complete_queue_item(result, thread_context)
            elif action == 'ignore':
                self.return_queue_item(item, thread_context)
            elif action == 'restart':
                new_item = result.queue_item.restart(extractor=new_extractor)
                self.push_queue_item(new_item, thread_context)
                self.complete_queue_item(result, thread_context)
            else:  # retry
                item.current_retries += 1
                # if new_extractor is not None and new_extractor != self.extractor:
                #     item.strategy = new_extractor
                self.refresh_queue_item(result.queue_item, new_extractor)

    def check_worker_state(self,) -> str:
        fetcher_state = self.fetcher.fetcher_state()
        if fetcher_state == 'working':
            self.state = 'working'
        else:
            self.state = 'idle'
        return self.state

    def fetcher_thread_loop(self, thread_num: int, wait_seconds: int = 30):
        context = self.new_thread_context()
        while self.state == 'working':
            self.throttle_request()
            # self.state_check_lock.acquire()
            item = self.pop_best_work_queue_item(context=context, wait_seconds=wait_seconds)
            if item is None:
                kl.trace(f'thread {thread_num}: no item available in queue')
                self.state = 'idle'
                # self.check_worker_state(force_recheck=False, sqs_client=sqs_client, wait_seconds=20)
                # self.state_check_lock.release()
            else:
                # self.state_check_lock.release()
                kl.trace(f'thread {thread_num}: read item from queue')
                self.process_item(item, context)
        kl.trace(f'thread {thread_num}: finished')

    def loop_pause(self):
        kl.trace(f'loop pause: {self.loop_pause_seconds} s')
        time.sleep(self.loop_pause_seconds)

    def worker_loop(self):
        while True:
            self.work()
            self.loop_pause()

    def work(self):
        self.check_worker_state()
        if self.state != 'working':
            kl.warn(f'Nothing to do: worker in state {self.state}')
            return

        threads = []
        for i in range(self.n_threads):
            t = threading.Thread(target=self.fetcher_thread_loop, args=(i, self.queue_wait_seconds,))
            t.start()
            threads.append(t)

        # wait for queue to be processed
        for t in threads:
            t.join()

        kl.info(f'worker for {self.extractor} finished: fetcher state {self.state}')


class KarnakSqsFetcherWorker(KarnakFetcherWorker):

    def __init(self, fetcher: KarnakSqsFetcher, extractor: str, n_threads: int = 1,
               loop_pause_seconds: int = 180, queue_wait_seconds: int = 30):
        self.sqs_fetcher = fetcher
        super().__init__(fetcher=fetcher,
                         extractor=extractor,
                         n_threads=n_threads,
                         loop_pause_seconds=loop_pause_seconds,
                         queue_wait_seconds=queue_wait_seconds)

    def pop_work_queue_item(self,
                            priority: Optional[int],
                            context: KarnakSqsFetcherThreadContext,
                            wait_seconds: int) -> Optional[KarnakFetcherQueueItem]:
        return self.sqs_fetcher.pop_work_queue_item(extractor=self.extractor,
                                                    priority=priority, context=context,
                                                    wait_seconds=wait_seconds)

    def pop_best_work_queue_item(self,
                                 context: KarnakSqsFetcherThreadContext,
                                 wait_seconds: int = 30) -> Optional[KarnakFetcherQueueItem]:
        return self.sqs_fetcher.pop_best_work_queue_item(extractor=self.extractor,
                                                         context=context,
                                                         wait_seconds=wait_seconds)

    @abstractmethod
    def return_queue_item(self, item: KarnakFetcherQueueItem, context: KarnakSqsFetcherThreadContext):
        queue_name = self.sqs_fetcher.worker_queue_name(extractor=item.extractor, priority=item.priority)
        ksqs.return_message(queue_name, item.handle, sqs_client=context.sqs_client)

    @abstractmethod
    def push_queue_item(self, item: KarnakFetcherQueueItem, context: KarnakSqsFetcherThreadContext):
        queue_name = self.sqs_fetcher.worker_queue_name(extractor=item.extractor, priority=item.priority)
        ksqs.send_messages(queue_name, [item.to_string()])

    @abstractmethod
    def refresh_queue_item(self, item: KarnakFetcherQueueItem,
                           context: KarnakSqsFetcherThreadContext,
                           new_extractor: str = None,
                           new_priority: int = None):
        _extractor = item.extractor if new_extractor is None else new_extractor
        _priority = item.priority if new_priority is None else new_priority
        old_queue_name = self.sqs_fetcher.worker_queue_name(extractor=item.extractor, priority=item.priority)
        new_queue_name = self.sqs_fetcher.worker_queue_name(extractor=_extractor, priority=_priority)
        new_item = item
        if new_extractor is not None:
            new_item = item.set_extractor(extractor=new_extractor)
        if new_priority is not None:
            new_item = item.set_priority(priority=new_priority)
        ksqs.send_messages(new_queue_name, [new_item.to_string()])
        ksqs.remove_message(old_queue_name, item.handle)

    @abstractmethod
    def complete_queue_item(self, result: KarnakFetcherResult, context: KarnakSqsFetcherThreadContext):
        """Put fetched results in queue (in case of success or failure with no retry)"""
        item = result.queue_item
        kl.trace(f'completing item: {item.key}')
        message_str = result.to_string()
        worker_queue_name = self.sqs_fetcher.worker_queue_name(extractor=item.extractor, priority=item.priority)
        try:
            if len(message_str) > 262144:
                kl.warn(f'message too long to put in queue, key: {item.key}, {len(item.to_string())} bytes')
            else:
                ksqs.send_messages(self.sqs_fetcher.results_queue_name(), [result.to_string()])
            ksqs.remove_message(worker_queue_name, item.handle)
        except Exception as e:
            kl.exception(f'exception putting message in results queue: {item.key}', e)
