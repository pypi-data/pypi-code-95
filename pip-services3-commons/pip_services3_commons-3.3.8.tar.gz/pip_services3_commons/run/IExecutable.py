# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.IExecutable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for executable components with parameters
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Optional

from pip_services3_commons.run import Parameters


class IExecutable(ABC):
    """
    Interface for components that can be called to execute work.

    .. code-block:: python
        class EchoComponent(IExecutable):
            ...
            def execute(self, correlation_id: Optional[str], args: Parameters):
                result = args.get_as_object("message")
                return result

        echo = new EchoComponent()
        message = "Test";
        result = echo.execute("123", Parameters.from_tuples("message", message))
        print("Request: " + message + " Response: " + result)

    """

    def execute(self, correlation_id: Optional[str], args: Parameters):
        """
        Executes component with arguments and receives execution result.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param args: execution arguments.

        :return: execution result
        """
        raise NotImplementedError('Method from interface definition')
