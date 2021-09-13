#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2020 Huawei Technologies Co., Ltd
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import acl
import os
import time
from cv2 import randShuffle
import numpy as np

from ..common.const import *
from ..common.path import check_file_exist
from functools import wraps
from prettytable import PrettyTable
from ..resource.context import bind_context

class Dump():
    """Define a Dump class to do model layer data dump and finetune model.
       It define a decorator running in model infer

    Attributes:
        context (int): Context resource
        model_id (int): The model_id that profiling will do.

    Methods:
        - profiling(func): do model profiling.
        - elapse_time(func): do function timling
        - info_print(sort=False): log infomation of profiling.

    Typical usage example:
    ```python
    debug = ascend.Debug(ctx, model.model_id)

    @debug.dump
    def run():
        model.run()

    run()
    ```
    """
    def __init__(self, context, cfg_path):
        if not isinstance(context, int):
            raise TypeError(f"Debug input context expects an int type, bug got {type(context)}.")

        bind_context(context)

        if cfg_path is None:
            raise ValueError(f"Input dump cfg_path should not be None.")
        else:
            check_file_exist(cfg_path)

        self._cfg_path = cfg_path
        self._context = context

        # profling data and info
        self.info = []

    def __enter__(self):
        """create a subcribe config, and subscribe a thread.

        Args:
            None

        Returns:
            None
        """
        # initial dump
        ret = acl.mdl.init_dump()
        if ret != ACL_SUCCESS:
            raise ValueError(f"Debug initial dump failed, return {ret}.")

        ret = acl.mdl.set_dump(self._cfg_path)
        if ret != ACL_SUCCESS:
            raise ValueError(f"Debug set dump of cfg_path failed, return {ret}.")

    def config():
        
    def _get_model_info(self, data, data_len):
        """ parser profiling data from memory and save to self.info

        Args:
            data    : the operators' information data
            data_len: the operators' information data size

        Returns:
            None
        """
        op_number, ret = acl.prof.get_op_num(data, data_len)
        if ret != ACL_SUCCESS:
            raise ValueError(f"get op num failed, return {ret}.")

        for i in range(op_number):
            # get model id that operator running
            model_id = acl.prof.get_model_id(data, data_len, i)

            # get type of i-th op
            op_type, ret = acl.prof.get_op_type(data, data_len, i, 65)
            assert ret == ACL_SUCCESS, f"get op type failed, return {ret}."

            # get name of i-th op
            op_name, ret = acl.prof.get_op_name(data, data_len, i, 275)
            assert ret == ACL_SUCCESS, f"get op type failed, return {ret}."

            # get running start time of i-th op
            op_start = acl.prof.get_op_start(data, data_len, i)

            # get running end time of i-th op
            op_end = acl.prof.get_op_end(data, data_len, i)

            # get runnning duration of i-th op
            op_duration = acl.prof.get_op_duration(data, data_len, i)

            # save profiling result
            self.info.append([model_id, op_name, op_type, op_start, op_end, op_duration])

    def info_print(self, sort=False):
        """Print profiling info to terminal

        Args:
            sort (bool, optional): Whether sort the profiling result or not. Defaults to False.

        Typical usage example:
        ```python
        prof.info_print(sort=True)
        ```     
        """
        items = ['id', 'op_name', 'op_type', 'time_start', 'time_end', 'time_elapse']
        table = PrettyTable(items)

        for item in self.info:
            table.add_row(item)
        
        percent = np.array([e[-1] for e in self.info])
        percent = np.around(100 * percent / percent.sum(), decimals=2)
        table.add_column('percent(%)', percent)
        
        print(table.get_string(sortby='time_elapse' if sort else None, reversesort=True))

    def _read_data(self, args):
        """ read profiling data to pipe and save on memory.

        Args:
            args : function input parameter
 
        Returns:
            None
        """
        fd, ctx = args

        # bind context resource
        bind_context(ctx)
        
        buffer_size, ret = acl.prof.get_op_desc_size()
        if ret != ACL_SUCCESS:
            raise ValueError(f"get op desc of size failed, return {ret}.")

        # caculate memory size for save op info
        data_len = buffer_size * 10

        # read profiling data from pipe, the data size maybe lower than buffer_size*N
        while True:
            data = os.read(fd, data_len)
            if len(data) == 0:
                break

            # malloc numpy data memory to save profiling data
            np_data = np.array(data)
            np_data_ptr = acl.util.numpy_to_ptr(np_data)

            # parser profiling data 
            size = np_data.itemsize * np_data.size
            self._get_model_info(np_data_ptr, size)

    def dump(self, func):
        """Start dump data thread.

        Args:
            func (obj): the function to do dump

        Returns:
            wrapped_function
        """
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            print(func.__name__ + " was called, and start profiling.")

            # start profiling
            with self:
                self._thread_id, ret = acl.util.start_thread(self._read_data, [self.r, self._context])
                if ret != ACL_SUCCESS:
                    raise ValueError(f"start tread {self._thread_id} failed, return {ret}.")
                
                return func(*args, **kwargs)

        return wrapped_function

    def elapse_time(self, func):
        """Print function excute time.

        Args:
            func (obj): The runing function.

        Returns:
            wrapped_function
        """        
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            print(func.__name__ + " was called, and start time.")
            
            start_time = time.time()
            res = func(*args, **kwargs)
            use_time = time.time() - start_time

            print(f"{func.__name__} elapse time:{use_time}")
            return res
        return wrapped_function


    def __exit__(self, exc_type, exc_value, traceback):
        """ unsubscribe thread and destroy subscribe config.

        Args:
            None

        Returns:
            None
        """
        if hasattr(self, '_model_id'):
            ret = acl.prof.model_un_subscribe(self._model_id)
            assert ret == ACL_SUCCESS, f"unsubscribe profiling thread failed, return {ret}."

        if hasattr(self, '_thread_id'):
            ret = acl.util.stop_thread(self._thread_id)
            assert ret == ACL_SUCCESS, f"stop thread {self._thread_id} failed, return {ret}."

        # close pipe
        os.close(self.r)

        ret = acl.prof.destroy_subscribe_config(self._subs_conf)
        if ret != ACL_SUCCESS:
            raise ValueError(f"destroy subscribe config of profiling failed, return {ret}.")

