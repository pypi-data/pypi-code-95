from .serialization import YAMLMixin
from .tasks import MicroTask


class DataConnector(YAMLMixin):
    """Encapsulates a data handler along with zero or more micro tasks.

    With the earliest access to the underlying data (through the `values` property), the class will first execute the
    micro tasks in the same order that they are defined in, and then stores the augmented volatile data internally.
    Tasks that attempt to access the data through this connector will receive the augmented data, while the original
    data handler remains intact.
    """

    def __init__(self, plainDataConnector, dataHandler):
        self.dataHandler = dataHandler
        self.augmentedVolatileData = None
        self.microTasks = [MicroTask.instantiate(plainMicroTask) for plainMicroTask in plainDataConnector.get('microTasks', {})]

    @property
    def values(self):
        if self.augmentedVolatileData is None:
            self.augmentedVolatileData = self.dataHandler.values  # Data handler will read from the source.
            for microTask in self.microTasks:
                self.augmentedVolatileData = microTask.execute(self.augmentedVolatileData)
        return self.augmentedVolatileData

    @values.setter
    def values(self, newValue):
        self.dataHandler.values = newValue  # Data handler will write back to the source.

    def toDict(self):
        return {}  # ToDo
