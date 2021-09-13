from munch import Munch

from .base import Persistent
from ..path import Path


class Reference(Persistent):
    """Raw reference to a persistent storage.

    References simply return the path to the storage as the gateways, leaving all required actions to the volatile
    counterpart. No more than a simple path is expected from the workflow description.
    """

    def __init__(self, plainStorage):
        path = plainStorage.get('path') if isinstance(plainStorage, Munch) else plainStorage
        self.path = Path(path)

    @property
    def readFrom(self):
        return self.path.raw

    @property
    def writeTo(self):
        return self.path.raw

    def toDict(self):
        return {'path': self.path.raw}
