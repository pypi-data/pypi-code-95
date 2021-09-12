import atexit
import threading
import multiprocessing

open_threads = []


class AsyncRunner:
    def __init__(self, func, process_mode=False):
        self.func = func
        self.process_mode = process_mode

        atexit.register(AsyncRunner.wait_fot_threads)

    def run(self, *args, **kwargs):
        thread = threading.Thread(
            target=self.suppressed_func,
            args=args,
            kwargs=kwargs
        )
        thread.start()

        global open_threads
        open_threads.append(thread)

    def suppressed_func(self, *args, **kwargs):
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            print("Caught Cnvrg Exception: {}".format(e))

    @staticmethod
    def wait_fot_threads():
        global open_threads
        for t in open_threads:
            t.join()
