import asyncio
import functools
import hashlib
import random
import string
from typing import Any


def md5(_str):
    """ md5 string """
    if isinstance(_str, bytes):
        return hashlib.md5(_str).hexdigest()
    elif isinstance(_str, str):
        return hashlib.md5(_str.encode()).hexdigest()


def rstr(n: int = 32) -> str:  # noqa
    """ random string """
    return ''.join(random.choices(
        string.digits + string.ascii_lowercase + string.ascii_uppercase,
        k=n
    ))


def rone(data) -> Any:  # noqa
    """ random one """
    if isinstance(data, (list, tuple)):
        return random.choice(data)
    elif isinstance(data, dict):
        return random.choice(list(data.items()))


def ip_to_int(ip: str):
    """ IP convert to int """
    # 192.168.1.13
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return functools.reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


def int_to_ip(ip: int) -> str:
    """ int ip num to ip str
        tmp1 = ip >> 24
        tmp2 = (ip >> 16) - (tmp1 << 8)
        tmp3 = (ip >> 8) - (tmp1 << 16) - (tmp2 << 8)
        tmp4 = ip - (tmp1 << 24) - (tmp2 << 16) - (tmp3 << 8)
    """

    def inner(lst=[], times=3):
        tmp = ip >> times * 8
        for idx, item in enumerate(reversed(lst)):
            tmp -= item << (idx + 1) * 8
        lst.append(tmp)
        if times > 0:
            return inner(times=times - 1)
        return lst

    return '{}.{}.{}.{}'.format(*inner())


class SingletonBase(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance  # noqa


def async_loop():
    try:
        loop = asyncio.get_event_loop()
    except:  # noqa
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


async def to_async(f, retry=True, *args, **kwargs):
    try:
        return await async_loop().run_in_executor(
            None, functools.partial(f, *args, **kwargs))
    except Exception as e:
        if retry:
            await asyncio.sleep(5)
            return await to_async(f, retry=False, *args, **kwargs)
        raise e


class SuperDict(dict):
    def __add__(self, other: dict):
        for k, v in other.items():
            self.__setitem__(k, v)
        return self

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = self.__class__() + value
        super(SuperDict, self).__setitem__(key, value)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except:  # noqa
            return self.get(item)
