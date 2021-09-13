from . import persistents, volatiles
from .serialization import YAMLMixin


class DataHandler(YAMLMixin):

    @staticmethod
    def inferStorage(plainDataHandler):
        return persistents.Reference, volatiles.PandasDataFrame

    def __init__(self, plainDataHandler):
        Persistent, Volatile = self.inferStorage(plainDataHandler)
        self.persistent = Persistent(plainDataHandler.get('persistent'))
        self.volatile = Volatile(plainDataHandler.get('volatile'))

    @property
    def values(self):
        if not self.volatile.ready:
            self.volatile.populate(self.persistent.readFrom)
        return self.volatile.values

    @values.setter
    def values(self, newValue):
        self.volatile.mutate(self.persistent.writeTo, newValue)

    def toDict(self):
        return {
            'persistent': self.persistent.toDict(),
            'volatile': self.volatile.toDict(),
        }
