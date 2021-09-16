from collections import defaultdict
from pyhectiqlab.timer import RepeatedTimer

import numpy as np
import threading
import pyhectiqlab.ops as ops
import time

class MetricsManager():

    def __init__(self, run_id,
        max_cache_timeout=5,  # seconds
        max_cache_length=100, # Number of elements
        min_cache_flush_delay=5, # Minimum number of seconds between a cache flush
        aggregate_metrics="none", # Wheter to push all data in cache or aggregate
        push_method=None):
        self._run = run_id
        self.cache = defaultdict(list)
        self.cache_last_push = {}

        self.max_cache_length = max_cache_length
        self.min_cache_flush_delay  = min_cache_flush_delay
        self.push_method = push_method
        self.set_aggr(aggregate_metrics)

        self.timer = RepeatedTimer(self.flush_cache, max_cache_timeout)
        self.timer.start()
        return

    def update_cache_settings(self, max_cache_timeout, max_cache_length, min_cache_flush_delay):
        if max_cache_timeout is not None:
            self.max_cache_timeout = max_cache_timeout
            self.timer.stop()
            self.timer = RepeatedTimer(self.flush_cache, max_cache_timeout)
            self.timer.start()
        if max_cache_length is not None:
            self.max_cache_length = max_cache_length
        if min_cache_flush_delay is not None:
            self.min_cache_flush_delay = min_cache_flush_delay
            
    def set_aggr(self, new_value):
        vals = ['none', 'sum', 'max', 'mean']
        assert new_value in vals, f"Aggr must be in {vals}"
        self.aggregate_metrics = new_value

    def add(self, key, value, step):
        if value is None:
            return
        self.cache[key].append((float(step), float(value)))
        if len(self.cache[key])>self.max_cache_length:
            if key in self.cache_last_push:
                last_push_time = self.cache_last_push[key]
                elapsed = time.time() - last_push_time
                if elapsed<self.min_cache_flush_delay:
                    return      
            self.push_data(key)

    def push_data(self, key):
        self.cache_last_push[key] = time.time()
        if self.aggregate_metrics=="none":
            self.push_method(key, self.cache[key])
        elif self.aggregate_metrics=="mean":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.mean(s)))])
        elif self.aggregate_metrics=="max":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.max(s)))])
        elif self.aggregate_metrics=="sum":
            k = [_[0] for _ in self.cache[key]]
            s = [_[1] for _ in self.cache[key]]
            if len(k) > 0:
                self.push_method(key, [(float(np.max(k)), float(np.sum(s)))])
        self.cache[key] = []


    def __delete__(self):
        self.timer.stop()
        self.flush_cache()

    def flush_cache(self):
        for key in self.cache:
            self.push_data(key)
