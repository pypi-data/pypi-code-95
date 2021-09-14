import sys
import asyncio
import logging
from threading import Thread

logger = logging.getLogger(__name__)


class Coro(Thread):
    def __init__(self):
        super().__init__(name='coroThread', daemon=False)
        self.loop = asyncio.new_event_loop()
        self.tasks = {}

    def run(self) -> None:
        try:
            asyncio.set_event_loop(self.loop)
        except:
            logger.error('协程启动失败')
            sys.exit()
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def add_task(self, coro, name=None):
        task = self.loop.create_task(coro, name=name)
        self.loop._csock.send(b'\0')
        name = task.get_name()
        self.tasks[name] = task
        return name

    def stop_task(self, name):
        self.tasks[name].cancel()

    def get_result(self, name):
        try:
            res = self.tasks[name].result()
        except Exception as e:
            res = str(e)
        return res

    def is_done(self, name):
        return self.tasks[name].done()
