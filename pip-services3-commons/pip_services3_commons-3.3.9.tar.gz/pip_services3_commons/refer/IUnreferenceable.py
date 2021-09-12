# -*- coding: utf-8 -*-
"""
    pip_services3_commons.refer.IUnreferenceable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for unreferenceable components.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC


class IUnreferenceable(ABC):
    """
    Interface for components that require explicit clearing of references to dependent components.

    Example:

    .. code-block:: python

        class MyController(IReferenceable):
            _persistence = None

            def set_references(self, references):
                self._persistence = references.getOneRequired(Descriptor("mygroup", "persistence", "*", "*", "1.0"))

            def unset_references(self):
                self._persistence = None

            
    """

    def unset_references(self):
        """
        Unsets (clears) previously set references to dependent components.
        """
        raise NotImplementedError('Method from interface definition')
