import abc

from munch import Munch

from ..serialization import YAMLMixin
from ..storage import Storage


class Persistent(Storage, YAMLMixin, abc.ABC):
    """Base class for persistent storages.

    A persistent storage must expose two *gateways*, one for reading from it, and one for writing to it. These will be
    defined in the form of two abstract property methods which must be overridden.

    Parameters
    ----------
    plainStorage: Munch
        Description for the persistent storage.
    """

    @abc.abstractmethod
    def __init__(self, plainStorage):
        pass

    @property
    @abc.abstractmethod
    def readFrom(self):
        """
        Gateway for reading from the persistent storage.
        """
        pass

    @property
    @abc.abstractmethod
    def writeTo(self):
        """
        Gateway for writing to the persistent storage.
        """
        pass
