"""Worker Log Bootstep."""
from celery import bootsteps
from collections import defaultdict
import threading
from queue import Queue
from celery.utils.log import get_logger

logger = get_logger(__name__)

__all__ = ('LogStep',)


class LogStep(bootsteps.StartStopStep):
    def __init__(self, c, **kwargs):
        c.log = None
        super().__init__(c, **kwargs)

    def start(self, c):
        c.log = _Logger()


class _Logger:
    buffer = defaultdict(dict)
    msg = Queue()
    worker: threading.Thread

    # def __init__(self):
    #     self.woker = threading.Thread(target=self.consume).start()

    def update(self, task_id, msg: dict):
        print(f"task id: {task_id}, msg: {msg}")

    def consume(self):
        while True:
            msg = self.msg.get()
            if msg is None:
                break

    def stop(self, parent):
        self.msg.put(None)
        self.worker.join()
