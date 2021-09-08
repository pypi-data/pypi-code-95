# -*- coding: utf-8 -*-
from typing import Any


class TargetException(Exception):
    pass


class NoDefault:
    pass


class Target:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.type = kwargs.get("type", Any)
        self.default = kwargs.get("default", NoDefault)

    @classmethod
    def output(cls, name, *args, **kwargs):
        """
        Define a new output target for a given class

        :param name: the target name
        :return: the class wrapper
        """

        def wrapper(TaskClass):
            if name == "__auto__":
                try:
                    # import these modules only if using auto output targets
                    import ast
                    import inspect
                    import textwrap

                    class Visitor(ast.NodeVisitor):
                        def visit_Return(self, node: ast.Return):
                            for output in node.value.keys:
                                TaskClass.add_output(
                                    cls(name=output.s, *args, **kwargs)
                                )

                    Visitor().visit(
                        ast.parse(textwrap.dedent(inspect.getsource(TaskClass.run)))
                    )
                    return TaskClass
                except Exception:
                    raise Exception(
                        f"Could not automatically determine outputs of task {TaskClass}. Check that this tasks "
                        f"returns a dictionary. To disable automatic task outputs, call Task constructor with "
                        f"auto_outputs=False "
                    )

            TaskClass.add_output(cls(name=name, *args, **kwargs))
            return TaskClass

        return wrapper

    @classmethod
    def input(cls, name, *args, **kwargs):
        """
        Define a new input target for a given class

        :param name: the target name
        :return: the class wrapper
        """

        def wrapper(TaskClass):
            TaskClass.add_input(cls(name=name, *args, **kwargs))
            return TaskClass

        return wrapper

    @classmethod
    def parameter(cls, name, *args, **kwargs):
        """
        Define a new input parameter for a given class

        :param name: the target name
        :return: the class wrapper
        """

        def wrapper(TaskClass):
            TaskClass.add_parameter(cls(name=name, *args, **kwargs))
            return TaskClass

        return wrapper

    @classmethod
    def parameters(cls, *names):
        """
        Define a list of input parameters for a given class

        :param names: the target names
        :return: the class wrapper
        """

        def wrapper(TaskClass):
            for name in names:
                TaskClass.add_parameter(cls(name=name))
            return TaskClass

        return wrapper
