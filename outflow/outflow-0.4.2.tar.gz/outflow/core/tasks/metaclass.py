# -*- coding: utf-8 -*-
import inspect
from typing import Any

from outflow.core.exceptions import ContextArgumentException, TaskWithKwargsException
from outflow.core.generic.string import to_snake_case
from outflow.core.plugin import get_plugin_name
from outflow.core.target import Target, NoDefault
from outflow.core.types import TargetOutputs, outputs_type_factory


class TaskMeta(type):
    def __new__(cls, name, bases, dct, *args, **kwargs):
        """Create a new Task class

        Args:
            name (str): name is the name of the newly created class
            bases (tuple): bases is a tuple of the class's base classes
            dct (dict): dct maps attribute names to objects, listing all of the class's attributes

        Returns:
            [type]: the new task class
        """

        if not dct.get("plugin_name", None):
            dct["plugin_name"] = get_plugin_name()

        # if the new class is a subclass of task but is not an executable task
        if "run" not in dct:
            return super().__new__(cls, name, bases, dct)
        # else continue ...

        # add an class attribute to specify if the task is passing self to the run method
        dct["with_self"] = dct.get("with_self", True)

        # if the return type is not defined, force it to Dict
        if dct["run"].__annotations__ is None:
            dct["run"].__annotations__ = dict()

        if "return" not in dct["run"].__annotations__:
            dct["run"].__annotations__.update({"return": TargetOutputs})

        return super().__new__(cls, name, bases, dct)

    def __init__(self, name, bases, dct):
        """Initialize the new Task class

        Args:
            name (str): name is the name of the newly created class
            bases (tuple): bases is a tuple of the class's base classes
            dct (dict): dct maps attribute names to objects, listing all of the class's attributes

        Returns:
            [type]: the initialized task class
        """

        self.name = to_snake_case(self.__name__)

        # get the names and default values of the run function parameters
        full_args_spec = inspect.getfullargspec(self.run)

        if full_args_spec.kwonlyargs:
            raise TaskWithKwargsException(
                f"Task '{self}' contains kwargs but task with kwargs are not allowed"
            )

        defaults = []
        for i in range(1, len(full_args_spec.args) + 1):
            try:
                defaults.append(full_args_spec.defaults[-i])
            except (IndexError, TypeError):
                defaults.append(NoDefault)
        defaults.reverse()

        # automatically add missing inputs (TODO: also add outputs using the type of the return dict)
        for index, input_arg_name in enumerate(full_args_spec.args):
            if self.with_self and index == 0:
                if input_arg_name != "self":
                    raise ContextArgumentException(
                        f"The task '{self}'' was declared with context but the first argument of the run method is not self"
                    )
                # skip the "self" argument for run class method
                continue

            annotations = full_args_spec.annotations
            if input_arg_name in annotations:
                input_type = annotations[input_arg_name]
            else:
                input_type = Any

            Target.input(input_arg_name, type=input_type, default=defaults[index])(self)

        return_annotation = full_args_spec.annotations.get("return", None)
        if isinstance(return_annotation, dict):
            for output_name, output_type in return_annotation.items():
                Target.output(output_name, type=output_type)(self)
            self.run.__annotations__["return"] = outputs_type_factory(return_annotation)

        # convert the run function to a static method if needed
        # Note: the typechecked decorator have to be applied before the static method decorator
        if not self.with_self:
            self.run = staticmethod(self.run)
