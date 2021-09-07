import asyncio
from typing import *  # noqa: F403

from netrunner.host import FailedHost, Host
from netrunner.runner import Response


class Task:
    def __init__(self, task: Callable, name: str, hosts: List[Host], response: Response, params: dict = None) -> None:
        self.task: Callable = task
        self.name: str = name
        self.hosts: List[Host] = hosts
        self.params: dict = params
        self.debug: bool = False
        self.response: Response = response

    async def _run_task(self, host: Host):
        if self.debug:
            print(f"Starting task for {host.hostname}")
        try:
            result = (
                await asyncio.create_task(self.task(host, **self.params))
                if self.params
                else await asyncio.create_task(self.task(host))
            )
            self.response.result[self.name].update({host.hostname: result})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.response.failed.append(FailedHost(host.hostname, host.ip, self.name, getattr(e, "message", str(e))))

    async def run_task(self, debug: bool):
        """Starts the task running"""
        self.debug = debug
        self.response.result.update({self.name: {}})

        await asyncio.gather(*[self._run_task(host) for host in self.hosts], return_exceptions=True)

    def _handle_task_result(self, task: asyncio.Task) -> None:
        """handles the asyncio task callback once task has finshed"""
        try:
            hostname = task.get_name().split(":")[1]
            self.response.result.update({hostname: task.result()})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            task_name, device, ip = task.get_name().split(":")
            self.response.failed.append(FailedHost(device, ip, task_name, getattr(e, "message", str(e))))
