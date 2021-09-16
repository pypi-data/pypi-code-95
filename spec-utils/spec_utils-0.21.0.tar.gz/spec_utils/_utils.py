import re
from asyncio import sleep as aio_sleep
from random import choice as r_choice
from string import digits as str_digits, ascii_lowercase as str_letters
from typing import Callable, Any, Generator, Optional

class Decorators:
    @staticmethod
    def ensure_session(method: Callable) -> Callable:
        def wrapper(client, *args, **kwargs) -> Optional[Any]:
            if client.session == None:
                raise ConnectionError(f"""
                    Start a session with self.start_session() before of make a 
                    request or use "with" expression like with 
                    {client.__class__.__name__}(url=...) as client: ...
                """)
            return method(client, *args, **kwargs)
        return wrapper

    @staticmethod
    def ensure_async_session(method: Callable) -> Callable:
        async def wrapper(clt, *args, **kwargs) -> Optional[Any]:
            if clt.session == None or getattr(clt.session, "closed", None):
                raise ConnectionError(f"""
                    Start a session with self.start_session() before of make a 
                    request or use "with" expression like async with 
                    {clt.__class__.__name__}(url=...) as client: ...
                """)
            return await method(clt, *args, **kwargs)
        return wrapper


def random_str(
    size: Optional[int] = 5,
    chars: Optional[str] = str_digits + str_letters
) -> str:
    """ Return a str of 'size' len with numbers and ascii lower letters. """

    return ''.join(r_choice(chars) for _ in range(size))


def create_random_suffix(name: Optional[str] = "") -> str:
    """ Create a random name adding suffix after of clean recived name. """

    clean = re.sub('[^a-zA-Z0-9]', '_', name)
    clean += '_' if name else "" 
    clean += random_str(size=5)

    return clean


async def async_range(
    start: int,
    stop: int = None,
    step: int = 1
) -> Generator:
    if stop:
        range_ = range(start, stop, step)
    else:
        range_ = range(start)
    for i in range_:
        yield i
        await aio_sleep(0)

