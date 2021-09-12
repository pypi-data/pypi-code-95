# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.Executor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Executor component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from .IExecutable import IExecutable
from .Parameters import Parameters


class Executor:
    """
    Helper class that executes components.
    """

    @staticmethod
    def execute_one(correlation_id: Optional[str], component: Any, args: Parameters):
        """
        Executes specific component.
        To be executed components must implement :class:`IExecutable <pip_services3_commons.run.IExecutable.IExecutable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param component: the component that is to be executed.

        :param args: execution arguments.

        :return: execution result
        """
        if isinstance(component, IExecutable):
            return component.execute(correlation_id, args)

        return None

    @staticmethod
    def execute(correlation_id: Optional[str], components: List[Any], args: Parameters = None):
        """
        Executes multiple components.

        To be executed components must implement :class:`IExecutable <pip_services3_commons.run.IExecutable.IExecutable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param components: a list of components that are to be executed.

        :param args: execution arguments.

        :return: execution result
        """
        results = []

        if components is None:
            return

        args = args if not (args is None) else Parameters()
        for component in components:
            result = Executor.execute_one(correlation_id, component, args)
            results.append(result)

        return results
