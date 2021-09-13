import abc

from munch import Munch

from ..serialization import YAMLMixin
from ..storage import Storage


class Volatile(Storage, YAMLMixin, abc.ABC):
    """Base class for volatile storages.

    A volatile storage must work in conjunction with the corresponding persistent storage, capable of performing reading
    and writing operations.

    Parameters
    ----------
    plainStorage: Munch
        Description for the volatile storage.
    """

    def __init__(self, plainStorage):
        self.values, self.ready = None, False
        self.importParameters = plainStorage.get('importParameters', Munch()) if plainStorage else Munch()
        self.exportParameters = plainStorage.get('exportParameters', Munch()) if plainStorage else Munch()

    # ToDo: Implement a mechanism to check before populating/mutating the data that it hasn't been mutated/populated before.

    @abc.abstractmethod
    def populate(self, gateway):
        pass

    @abc.abstractmethod
    def mutate(self, gateway, newValue):
        pass
