# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.ICleanable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for cleanable components
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Optional


class ICleanable(ABC):
    """
    Interface for components that should clean their state.
    Cleaning state most often is used during testing.
    But there may be situations when it can be done in production.

    .. code-block:: python
        class MyObjectWithState(ICleanable):
            _state = {}
            ...

            def clear(self, correlation_id):
                self._state = {}
    """

    def clear(self, correlation_id: Optional[str]):
        """
        Clears component state.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        raise NotImplementedError('Method from interface definition')
