from logging import getLogger

logger = getLogger(__name__)


def exclusive(function: callable):
    async def _wrapper(self, *args, **kwargs):
        async with self.lock:
            return await function(*args, **kwargs)

    return _wrapper
