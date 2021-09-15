#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import os
from multiprocessing.pool import ThreadPool

import dask
from dask.distributed import Client

_default_dask_threadpool_size = 50
_client = None
_storage = None


class MLRuntime(object):
    def __init__(self):
        dask_threadpool_size = (
            os.environ.get("DASK_THREADPOOL_SIZE") or _default_dask_threadpool_size
        )
        dask.config.set(pool=ThreadPool(int(dask_threadpool_size)))
        self.dask_client = Client(
            processes=False, local_directory="/tmp"  # use directory with write permits
        )

    def get_compute_accelerator(self):
        return self.dask_client


def init():
    global _client

    # ensures the client is created only once
    _client = MLRuntime().get_compute_accelerator()


def compute_accelerator():
    global _client
    if _client is None:
        init()
    return _client
