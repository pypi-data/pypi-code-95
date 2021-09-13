import abc
from pydoc import locate

from munch import Munch
from stringcase import snakecase, pascalcase

from .base import TaskBase


class MicroTask(TaskBase, abc.ABC):
    """Base class for micro-tasks.

    Subclass this class and override the `execute()` method to define a custom task and reference it in the workflow.
    """

    def __init__(self, parameters):
        self.parameters = parameters

    @abc.abstractmethod
    def execute(self, volatileData):
        pass

    @staticmethod
    def instantiate(plainMicroTask):
        spec = plainMicroTask.spec if isinstance(plainMicroTask, Munch) else plainMicroTask
        path = f'micro_tasks.{snakecase(spec)}.{pascalcase(spec)}'
        cls = locate(path)
        assert cls is not None, f'Could not import {path}'
        # noinspection PyCallingNonCallable
        return cls(parameters=plainMicroTask.get('parameters') if isinstance(plainMicroTask, Munch) else {})
