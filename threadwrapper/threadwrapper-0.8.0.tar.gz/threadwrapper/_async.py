import asyncio
# import nest_asyncio
import traceback
import time
import sys


__ALL__ = ["ThreadWrapper_async"]


class ThreadWrapper_async:
    def __init__(self, semaphore: asyncio.Semaphore, loop: asyncio.AbstractEventLoop) -> None:
        self.total_thread_count = 0
        self.sema = semaphore
        self.tasks = []
        self.loop = loop
        # nest_asyncio.apply(self.loop)
        self.debug_time = False

    async def __run_job(self, job: asyncio.coroutine, result, key):
        response = None
        try:
            await self.sema.acquire()
            start_time = time.time()
            response = await job
            if isinstance(result, list):
                result.append(response)
            elif isinstance(result, dict):
                result[key] = response
            duration = time.time()-start_time
            if self.debug_time:
                count = str(self.total_thread_count).ljust(20)
                qualname = job.__qualname__.ljust(50)
                timestamp = str(int(time.time() * 1000) / 1000).ljust(20)[6:]
                s = f"Thread {count}{qualname}{timestamp}{duration}s\n"
                if duration >= 0.5:
                    sys.stderr.write(s)
                    sys.stderr.flush()
                else:
                    print(s, flush=True)
        except:
            response = traceback.print_exc()
        finally:
            self.sema.release()
            return response

    def add(self, job: asyncio.coroutine, result = None, key = None):
        if result is None:
            result = {}
        if key is None:
            key = 0
        job = self.__run_job(job, result, key)
        job = asyncio.ensure_future(job, loop=self.loop)
        self.tasks.append(job)
        return True

    async def cleanup(self):
        cancelled = []
        for task in self.tasks:
            try:
                if not task.done():
                    task.cancel()
                    cancelled.append(task)
            except:
                pass
        try:
            if not cancelled:
                return
            tasks, _ = await asyncio.wait(cancelled, loop=self.loop)
            for task in tasks:
                try:
                    await task.result()
                except:
                    pass
        except:
            pass
        finally:
            await self.loop.shutdown_asyncgens()

    def wait(self, run_type=None):
        async def main():
            return await asyncio.gather(*self.tasks, loop=self.loop)

        asyncio.set_event_loop(self.loop)
        result = None
        try:
            if run_type == "run_forever":
                self.loop.run_forever()
            else:
                self.loop.run_until_complete(main())
        except KeyboardInterrupt:
            pass
        except:
            result = traceback.format_exc()
        self.loop.run_until_complete(self.cleanup())
        return result
