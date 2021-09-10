from typing import Callable

from jetpack import _job
from jetpack._job import client as _client
from jetpack._job.job import Job as _Job
from jetpack._remote.codec import FuncArgs


class JobDecorator:
    def __call__(self, fn: Callable) -> Callable:
        return _Job(fn)


job = JobDecorator()
