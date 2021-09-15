import zipfile
import os
from contextlib import contextmanager
from functools import lru_cache


class DataSource:
    def __init__(self, path: str):
        self.path = path
        if not os.path.isdir(path):
            self._archive: zipfile.ZipFile = zipfile.ZipFile(self.path, mode='r')
        else:
            self._archive = None

    @contextmanager
    def open(self, file):
        if self._archive:
            f = self._archive.open(file, 'r')
        else:
            f = open(os.path.join(self.path, file), mode='rb')
        try:
            yield f
        finally:
            f.close()

    @lru_cache
    def listdir(self):
        if self._archive:
            return self._archive.namelist()
        else:
            return os.listdir(self.path)

    def __repr__(self):
        if self._archive:
            return f'<DataSource @ {self.path} (Zip archive)>'
        else:
            return f'<DataSource @ {self.path}>'
