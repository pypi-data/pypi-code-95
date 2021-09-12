# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.Cleaner
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Cleaner component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from .ICleanable import ICleanable


class Cleaner:
    """
    Helper class that cleans stored object state.
    """

    @staticmethod
    def clear_one(correlation_id: Optional[str], component: Any):
        """
        Clears state of specific component.

        To be cleaned state components must implement :class:`ICleanable <pip_services3_commons.run.ICleanable.ICleanable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param component: the component that is to be cleaned.

        """
        if isinstance(component, ICleanable):
            component.clear(correlation_id)

    @staticmethod
    def clear(correlation_id: Optional[str], components: List[Any]):
        """
        Clears state of multiple components.

        To be cleaned state components must implement :class:`ICleanable <pip_services3_commons.run.ICleanable.ICleanable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param components: the list of components that are to be cleaned.
        """
        if components is None:
            return

        for component in components:
            Cleaner.clear_one(correlation_id, component)
