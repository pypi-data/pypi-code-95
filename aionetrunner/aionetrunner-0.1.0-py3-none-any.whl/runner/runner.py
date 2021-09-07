import asyncio
from time import perf_counter
from typing import *  # noqa: F403

from netrunner.host import Host
from netrunner.runner import Credentials, Response
from netrunner.runner.errors import (InvalidHostKeys, InvalidTask,
                                     NoHostsPresent)
from netrunner.task import Task


class Runner:
    """Task runner"""

    def __init__(
        self, username: str, password: str, enable: Optional[str] = None, hosts: List[Dict] = None, debug: bool = False
    ) -> None:
        """Initialise task runner. Requires username and password"""
        self.credentials: Credentials = Credentials(username=username, password=password, enable=enable)
        self.hosts: list[Host] = self.get_hosts(hosts) if hosts else []
        self.debug: bool = debug
        self.tasks: Set[Task] = set()
        self.response: Response = Response()

    def get_hosts(self, hosts: List[Dict]) -> None:
        """Add hosts to host list"""
        try:
            hosts = [
                Host(hostname=host["hostname"], ip=host["ip"], platform=host["platform"], credentials=self.credentials)
                for host in hosts
            ]
        except KeyError:
            raise InvalidHostKeys("Invalid or missing keys in host list")
        return hosts

    def _validate_task(self, name: str, task: Callable, hosts: List[Dict]) -> bool:
        if not isinstance(task, Callable):
            raise InvalidTask(f"{name}: Task must be a function")
        if len(self.hosts) == 0 and not hosts:
            raise NoHostsPresent("No hosts have been passed to the runner.")
        return True

    def queue_task(self, name: str, task: Callable, hosts: List[Dict] = None, **params) -> None:
        """Add task to pending task list, if no hosts are passed into the function,
        the class hosts will be used"""
        if self._validate_task(name, task, hosts):
            task_hosts = self.get_hosts(hosts) if hosts else self.hosts
            self.tasks.add(Task(name=name, task=task, hosts=task_hosts, response=self.response, params=params))

    async def run(self, name: str = None, task: Callable = None, hosts: List[Dict] = None, **params) -> Response:
        """run tasks in the pending tasks queue"""
        if any([name, task, hosts]):
            self.queue_task(name, task, hosts, **params)

        self.response.start_time = perf_counter()
        await asyncio.gather(*[task.run_task(self.debug) for task in self.tasks])
        self.response.end_time = perf_counter()
        return self.response
