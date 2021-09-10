from queue import Queue
from sys import stdout

from aiohttp import ClientSession

from air_kit.process import Process

telemetry = None


def get_telemetry():
    global telemetry
    return telemetry


def set_telemetry(telemetry_new):
    global telemetry
    telemetry = telemetry_new


class TelemetryStream:
    def __init__(
        self,
        is_stdout: bool = True,
        is_telemetry: bool = True,
    ):
        self.is_stdout = is_stdout
        self.is_telemetry = is_telemetry

    def write(self, data):
        if self.is_stdout:
            stdout.write(data)

        if self.is_telemetry and get_telemetry():
            get_telemetry().enqueue(data)

    def flush(self):
        if self.is_stdout:
            stdout.flush()


class TelemetryProcess(Process):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.queue = Queue()

        super().__init__("telemetry", period=3.0)

    def enqueue(self, data):
        self.queue.put(data)

    async def _on_start(self) -> None:
        pass

    async def _on_stop(self) -> None:
        await self._flush()

    async def _activity(self):
        await self._flush()

    async def _flush(self):
        if self.queue.empty():
            return

        buffer = []

        while not self.queue.empty():
            buffer.append(self.queue.get()[:-1])

        # TODO: check response ok
        # TODO: handle exceptions

        async with ClientSession() as session:
            async with session.post(
                f"http://{self.host}:{self.port}/logs",
                json={
                    "items": buffer,
                },
            ) as _:
                pass
