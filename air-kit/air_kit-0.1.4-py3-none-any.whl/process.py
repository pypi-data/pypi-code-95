from asyncio import run, sleep
from logging import getLogger
from multiprocessing import Process as BaseProcess
from multiprocessing import Value

logger = getLogger(__name__)


class Process(BaseProcess):
    def __init__(self, name: str, *, period: float = 1.0, **kwargs):
        self.name = name
        self.period = period
        self.is_active = Value("b", 1)

        super().__init__(name=name, args=(self.is_active,), kwargs=kwargs)

    def start(self) -> None:
        super().start()

    def stop(self) -> None:
        self.is_active.value = 0
        self.join()

    def run(self) -> None:
        try:
            run(self._run())
        except BaseException:
            logger.exception(f"Exception in process {self.name} loop.")
            pass

    async def _run(self) -> None:
        # Getting multiprocess parameters.
        self.is_active = self._args[0]

        for name, value in self._kwargs.items():
            setattr(self, name, value)

        # Start.
        await self._on_start()
        logger.debug(f"Process id {self.pid}, name {self.name} started.")

        # Running.
        await self._loop()

        # Stop.
        await self._on_stop()
        logger.debug(f"Process id {self.pid}, name {self.name} stopped.")

    async def _loop(self) -> None:
        while self.is_active.value:
            try:
                await self._activity()
                await sleep(self.period)
            except BaseException:
                logger.exception(
                    f"Exception while running process id {self.pid}, name {self.name}."
                )
                await sleep(1)

    async def _on_start(self) -> None:
        pass

    async def _on_stop(self) -> None:
        pass

    async def _activity(self) -> None:
        pass
