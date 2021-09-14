import time
import threading
from debugging import *
from omnitools import list_or_dict, p


__ALL__ = ["Threadswrapper", "args"]


class ThreadWrapper:
    def __init__(self, semaphore: threading.Semaphore) -> None:
        self.total_thread_count = 0
        self.threads = []
        self.sema = semaphore
        self.debug_time = False

    def __run_job(self, job: Callable[[], Any], result: list_or_dict = None,
                  key: Any = None) -> None:
        self.sema.acquire()
        try:
            start_time = time.time()
            self.total_thread_count += 1
            if isinstance(result, list):
                result.append(job())
            elif isinstance(result, dict):
                result[key] = job()
            duration = time.time()-start_time
            if self.debug_time:
                count = str(self.total_thread_count).ljust(20)
                qualname = job.__qualname__.ljust(50)
                timestamp = str(int(time.time() * 1000) / 1000).ljust(20)[6:]
                s = "Thread {}{}{}{}s\n".format(count, qualname, timestamp, duration)
                if duration >= 0.5:
                    sys.stderr.write(s)
                    sys.stderr.flush()
                else:
                    p(s)
        except:
            p(debug_info()[0])
        finally:
            self.sema.release()

    def add(self, job: Callable[[], Any], result: list_or_dict = None,
            key: Any = None) -> bool:
        if result is None:
            result = {}
        if key is None:
            key = 0
        thread = threading.Thread(target=self.__run_job, args=(job, result, key))
        self.threads.append(thread)
        thread.start()
        return True

    def wait(self) -> bool:
        for thread in self.threads:
            thread.join()
        return True



