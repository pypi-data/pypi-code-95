import sys
from time import time
from typing import Any

from expiringdict import ExpiringDict

DEFAULT_MAX_ITEMS: int = 1000
DEFAULT_MAX_AGE_SECONDS: int = 60


def _fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return (_fib(n-1) + _fib(n-2))


class Cache(object):
    def __init__(self, max_items: int = DEFAULT_MAX_ITEMS, max_age_secs: int = DEFAULT_MAX_AGE_SECONDS) -> None:
        self.cache = ExpiringDict(
            max_len=max_items, max_age_seconds=max_age_secs)

    def get(self, key: str) -> Any:
        self._burn_cpu()
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._burn_cpu()
        self.cache[key] = value

    def info(self) -> dict:
        return {
            'num_cache_items': len(self.cache),
            'total_cache_size': sys.getsizeof(self.cache)
        }

    def _burn_cpu(self):
        start_time = time()
        n: int = 0

        while (time() - start_time) < 2:
            _value = _fib(n)
            n += 1
