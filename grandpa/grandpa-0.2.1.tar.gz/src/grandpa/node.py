import multiprocessing
import threading

from grandpa.routing import Switch
from grandpa.utils.utils import print_warning, filter_kwargs
import random


class NodeCache:
    """
    Class used for result caching.
    """
    def __init__(self, cache_size=multiprocessing.cpu_count()):
        self.cached_values = []
        self.cache_ids = []
        self.cache_size = cache_size

    def save(self, id, value):
        """
        Saves data to the cache.

        Args:
            id: ID of the data point.
            value: Value of the data point.

        Returns:
            None
        """
        if len(self.cache_ids) >= self.cache_size:
            del self.cached_values[0]
            del self.cache_ids[0]
        self.cached_values.append(value)
        self.cache_ids.append(id)

    def contains(self, id):
        """
        Checks if the given ID exists in the cache.

        Args:
            id: ID to search for.

        Returns:
            True if the ID is cached, else False.
        """
        return id in self.cache_ids

    def __call__(self, id):
        """
        Reads the ID's value from the cache.

        Args:
            id: ID to read.

        Returns:
            Value of the ID or None, if ID doesn't exist.
        """
        if id in self.cache_ids:
            return self.cached_values[self.cache_ids.index(id)]


class Node:
    """
    Parent class for all graph Nodes. All Nodes written by the user must inherit this class.
    """
    def __init__(self, address, main_router):
        self.nodes = {}
        self.address = address
        self.params = {}
        self.settings = {}
        self.switch = Switch(address, self, main_router)
        self.thread_lock = threading.Lock()
        print(f'Created new node {self.address}')
        self.cache = NodeCache()

    def add_node(self, name, node):
        """
        Adds a dependency node to this node.

        Args:
            name: Name as which the value should be passed in at run.
            node: The dependency node.

        Returns:
            None
        """
        self.__check_if_node_already_exists(name)
        self.nodes[name] = '//' + node.address

    def add_param(self, name, default='__required__'):
        self.params[name] = default

    def add_setting(self, name, value):
        self.settings[name] = value
        return value

    def _validate_params(self, params):
        for req_param, default in self.params.items():
            if req_param not in params:
                if default != '__required__':
                    params[req_param] = default
                else:
                    raise ValueError(f'The required param {req_param} for {self.address} was not set in graph '
                                     f'definition and no default was provided.')
        return params

    def has_param(self, name):
        return name in self.params

    def __check_if_node_already_exists(self, name):
        if name in self.nodes:
            print_warning(f'Parameter {name} for node {self.address} has already been set - '
                          f'previous value will be overridden.')

    def __call_sub_nodes_threaded(self, call_params, nodes, call_id):
        tasks = {}
        for name, node in nodes.items():
            tasks[name] = self.switch.execute_task(node, **{"call_id": call_id, **call_params})
        result = {name: t.get_result() for name, t in tasks.items()}
        return result

    def run(self, *args, **kwargs):
        raise NotImplementedError('run() must be implemented in sub classes of Node.')

    def run_with_call_id(self, *args, call_id=None, **call_params):
        run_nodes = {name: self.switch.get_instruction(node) for name, node in self.nodes.items() if
                     name not in call_params}
        params = self.__call_sub_nodes_threaded(call_params=call_params, nodes=run_nodes, call_id=call_id)
        filtered_call_params = filter_kwargs(self.run, call_params)
        params = {**params, **filtered_call_params}
        # params = self._validate_params(params)
        return self.run(*args, **params)

    def __call__(self, *args, call_id=None, **call_params):
        """
        Executes the node.

        Args:
            *args: Arguments to pass to this node.
            call_id: ID of the call. Usually assigned automatically by the framework.
            **call_params: Parameters to pass to the node at call.

        Returns:
            Result delivered by the node.
        """
        self.thread_lock.acquire()
        if call_id is None:
            call_id = random.getrandbits(128)
        if self.cache.contains(call_id):
            ret_value = self.cache(call_id)
        else:
            ret_value = self.run_with_call_id(*args, call_id=call_id, **call_params)
            self.cache.save(call_id, ret_value)
        self.thread_lock.release()
        return ret_value
