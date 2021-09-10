import asyncio
import contextvars
import functools
import nest_asyncio

from parallely.base import ParalellyFunction
from parallely.utils import prepare_arguments


class AsyncedFunction(ParalellyFunction):
    def __init__(self, func, max_workers):
        super().__init__(func, max_workers)
        nest_asyncio.apply()

    async def _to_thread(self, func, *args, **kwargs):
        """Asynchronously run function *func* in a separate thread.
        Any *args and **kwargs supplied for this function are directly passed
        to *func*. Also, the current :class:`contextvars.Context` is propogated,
        allowing context variables from the main thread to be accessed in the
        separate thread.
        Return a coroutine that can be awaited to get the eventual result of *func*.
        """
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            loop = asyncio.get_running_loop()
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, func, *args, **kwargs)
            return await loop.run_in_executor(None, func_call)

    async def _execute_once_async(self, func, sem, *args, **kwargs):
        if sem is not None:
            async with sem:  # semaphore limits num of simultaneous downloads
                return await self._to_thread(func, *args, **kwargs)
        else:
            return await self._to_thread(func, *args, **kwargs)

    def _execute_once(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._to_thread(self._func, *args, **kwargs))

    def map(self, *args, **kwargs):
        async def _async_map(func, *args, **kwargs):
            args, kwargs = prepare_arguments(args, kwargs)
            sem = asyncio.Semaphore(self._max_workers) if self._max_workers else None
            coros = []
            for arg_row, kwarg_row in zip(args, kwargs):
                coros.append(self._execute_once_async(func, sem, *arg_row, **kwarg_row))

            return await asyncio.gather(*coros)

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_map(self._func, *args, **kwargs))


def asynced(func=None, max_workers=None):
    if func is None:
        return functools.partial(asynced, max_workers=max_workers)

    return AsyncedFunction(func, max_workers)
