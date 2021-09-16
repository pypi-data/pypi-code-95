import os
from contextlib import contextmanager as _contextmanager
from datetime import date as _date_t
from datetime import datetime as _datetime_t


@_contextmanager
def chdir(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


class SortDate:
    def __init__(self, page):
        self.ts = None
        if page.metadata:
            self.ts = page.metadata.timestamp

    def __lt__(self, other):
        if self.ts and other.ts:
            return self.ts < other.ts
        return self.ts and not other.ts
