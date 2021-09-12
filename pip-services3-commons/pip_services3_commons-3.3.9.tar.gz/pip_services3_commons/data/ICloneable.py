# -*- coding: utf-8 -*-
"""
    pip_services3_commons.data.ICloneable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Interface for cloneable data objects

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any


class ICloneable:
    """
    Interface for data objects that are able to create their full binary copy.

    Example:

    .. code-block:: python

        class MyClass(IMyClass, ICloneable):
            def __init__():
                

            def clone(self):
                clone_obj = self.__init__()
                

                return clone_obj

    """
    def clone(self) -> Any:
        """
        Creates a binary clone of this object.

        :return: a clone of this object.
        """
        pass