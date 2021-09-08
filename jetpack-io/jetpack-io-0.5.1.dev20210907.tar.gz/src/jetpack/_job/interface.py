from typing import Callable

from jetpack import _job
from jetpack._job import client as _client
from jetpack._job.job import Job as _Job
from jetpack._remote.codec import FuncArgs


class JobDecorator:
    def __call__(self, fn: Callable) -> Callable:
        return _Job(fn)

    @classmethod
    def launch(cls, qualified_name: str, module: str = "", args: FuncArgs = None):
        if args:
            _client.launch_job(qualified_name, module, args[0], args[1])
        else:
            _client.launch_job(qualified_name, module)

    @classmethod
    def launch_blocking(
        cls, qualified_name: str, module: str = "", args: FuncArgs = None
    ):
        # Question: should we set the _client.LaunchJobMode here itself?
        if args:
            _client.launch_blocking_job(qualified_name, module, args[0], args[1])
        else:
            _client.launch_blocking_job(qualified_name, module)

    @classmethod
    def args(cls, *pargs, **kwargs) -> FuncArgs:
        return FuncArgs(
            args=pargs if pargs else None,
            kwargs=kwargs if kwargs else None,
        )


job = JobDecorator()
