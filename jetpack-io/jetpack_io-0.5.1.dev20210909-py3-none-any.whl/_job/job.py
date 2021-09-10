from __future__ import annotations

import asyncio
import base64
import inspect
import os
from typing import Callable, Dict, Optional, ValuesView

from jetpack import utils
from jetpack._job import client as _client
from jetpack._job import interface
from jetpack._remote import codec


class AlreadyExistsError(Exception):
    pass


class Job:
    # Question: do we need a separate Dict for blocking jobs?
    jobs: Dict[str, Job] = {}

    def __init__(self, func: Callable):
        self.func = func
        Job.add_job(self)

    def __call__(self, *args, **kwargs):
        """
        No return value for now, but eventually this will return a handle
        or an awaitable

        For now only self module is allowed. JETPACK_MODULE_ID must be set.
        """
        module_id = os.environ["JETPACK_MODULE_ID"]
        if inspect.iscoroutinefunction(self.func):
            return _client.launch_async_job(self.name(), module_id, args, kwargs)
        else:
            return _client.launch_job(self.name(), module_id, args, kwargs)

    def fire_and_forget(self, *args, **kwargs):
        module_id = os.environ["JETPACK_MODULE_ID"]
        if inspect.iscoroutinefunction(self.func):
            return _client.launch_fire_and_forget_async_job(
                self.name(), module_id, args, kwargs
            )
        else:
            return _client.launch_fire_and_forget_job(
                self.name(), module_id, args, kwargs
            )

    def name(self) -> str:
        return utils.qualified_func_name(self.func)

    def exec(self, base64_encoded_args: str = "") -> str:

        args, kwargs = None, None
        if base64_encoded_args:
            encoded_args = base64.b64decode(base64_encoded_args).decode("utf-8")
            args, kwargs = codec.decode_args(encoded_args)

        # ensure we default since encoded args might have None in them
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        if inspect.iscoroutinefunction(self.func):
            result = asyncio.run(self.func(*args, **kwargs))
        else:
            result = self.func(*args, **kwargs)
        # for now just return encoded result, but we could send it to a redis channel
        # that the caller might be listening to.
        return codec.encode_result(result)

    @classmethod
    def add_job(cls, job: Job):
        if job.name() in cls.jobs:
            raise AlreadyExistsError(f"Job with name {job.name()} already exists")
        cls.jobs[job.name()] = job

    @classmethod
    def find_job(cls, name: str) -> Optional[Job]:
        return cls.jobs.get(name)

    @classmethod
    def defined_jobs(cls) -> ValuesView[Job]:
        return cls.jobs.values()
