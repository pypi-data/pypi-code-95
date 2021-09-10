from threading import Lock
from collections import UserList
from regia.utils import SingleTon


class List(UserList):
    """
    List is a collection which is thread safe.
    """

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.lock = Lock()

    def append(self, item):
        self.lock.acquire()
        super(List, self).append(item)
        self.lock.release()


class SingleTonList(SingleTon, List):
    pass


class Mapping(SingleTon):
    mapping = []
    lock = Lock()
    path = set()

    def register(self, item: dict):
        self.lock.acquire()
        self.__class__.mapping.append(item)
        self.lock.release()

    def add_path(self, package):
        self.lock.acquire()
        self.__class__.path.add(package)
        self.lock.release()

    def __iter__(self):
        for item in self.mapping:
            yield item

    def __getitem__(self, item):
        return self.mapping[item]
