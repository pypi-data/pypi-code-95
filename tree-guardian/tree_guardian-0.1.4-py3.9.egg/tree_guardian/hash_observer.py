import os
import re
import time
import hashlib

from typing import Iterable, Callable, Dict
from threading import Event


class HashObserver(object):

    def __init__(self, path: str = '.', exclude: Iterable[str] = None, frequency: float = 0.1):
        if frequency <= 0.0:
            raise ValueError(f'Frequency should be great than zero; got {frequency}')
        
        self.path = path
        self.excluded = set(exclude or {})
        self.frequency = frequency

        self._stopped = False

    def filter_excluded(self, names: Iterable) -> Iterable:
        def regex_excluded(item):
            for exclude in self.excluded:
                if '*' in exclude and re.match(exclude.replace('*', '(.*)'), item):
                    return True
            return False

        res = []
        for name in names:
            if name in self.excluded or regex_excluded(name):
                continue
            res.append(name)

        return res

    def walk(self, abspath: str):
        if not os.path.isdir(abspath):
            return [abspath, ]

        res = []
        items = self.filter_excluded(os.listdir(abspath))
        for item in items:
            res.extend(self.walk(os.path.join(abspath, item)))

        return res

    @property
    def hash(self):
        path_hash = hashlib.md5()
        for filepath in self.walk(os.path.abspath(self.path)):
            try:
                with open(filepath, 'rb') as file:
                    filehash = hashlib.md5(file.read()).hexdigest()
                    path_hash.update(filehash.encode())
            except Exception as e:
                print(f'Error {e}')

        return path_hash.hexdigest()

    def observe(self, callback: Callable, event: Event = None,
                args: Iterable = None, kwargs: Dict = None):
        args = args or []
        kwargs = kwargs or {}

        hsh = self.hash
        self._stopped = False

        while not self._stopped:
            time.sleep(self.frequency)

            if event and event.set():
                self.stop()
                break

            if self.hash == hsh:
                continue

            hsh = self.hash
            callback(*args, **kwargs)

    def stop(self):
        self._stopped = True
