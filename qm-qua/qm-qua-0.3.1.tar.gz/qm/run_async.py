import asyncio
import threading


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        thread = RunThread(coro)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(coro)


class RunThread(threading.Thread):
    def __init__(self, func):
        self.func = func
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func)
