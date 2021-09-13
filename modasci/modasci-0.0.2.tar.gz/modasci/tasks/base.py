import abc

from ..serialization import YAMLMixin


class TaskBase(YAMLMixin, abc.ABC):
    """Base class for all types of tasks.

    The class is an interface for the common attributes and methods of all tasks.
    """
    pass
