# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.IOpenable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for openable components
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from .IClosable import IClosable


class IOpenable(IClosable):
    """
    Interface for components that require explicit opening and closing.
    For components that perform opening on demand consider using :class:`IClosable <pip_services3_commons.run.IClosable.IClosable>` interface instead.

    .. code-block:: python
        class MyPersistence(IOpenable):
            _client = None
            ...
            def is_open(self):
                return self._client is not None

            def open(correlation_id):
                if self.is_open()
                    return
                ...

            def close(self, correlation_id):
                if self._client is not None:
                    self._client.close()
                    self._client = None
            ...
    """

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        raise NotImplementedError('Method from interface definition')

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        raise NotImplementedError('Method from interface definition')
