# -*- coding: utf-8 -*-
"""
    pip_services3_commons.refer.Referencer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Referencer component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List

from pip_services3_commons.refer import IReferences
from .IReferenceable import IReferenceable
from .IUnreferenceable import IUnreferenceable


class Referencer:
    """
    Helper class that sets and unsets references to components.
    """

    @staticmethod
    def set_references_for_one(references: IReferences, component: Any):
        """
        Sets references to specific component.

        To set references components must implement :class:`IReferenceable <pip_services3_commons.refer.IReferenceable.IReferenceable>` interface.
        If they don't the call to this method has no effect.

        :param references: the references to be set.

        :param component: the component to set references to.
        """
        if isinstance(component, IReferenceable):
            component.set_references(references)

    @staticmethod
    def set_references(references: IReferences, components: List[Any]):
        """
        Sets references to multiple components.

        To set references components must implement :class:`IReferenceable <pip_services3_commons.refer.IReferenceable.IReferenceable>` interface.
        If they don't the call to this method has no effect.

        :param references: the references to be set.

        :param components: a list of components to set the references to.
        """
        if components is None:
            return

        for component in components:
            Referencer.set_references_for_one(references, component)

    @staticmethod
    def unset_references_for_one(component: Any):
        """
        Unsets references in specific component.

        To unset references components must implement :class:`IUnreferenceable <pip_services3_commons.refer.IUnreferenceable.IUnreferenceable>` interface.
        If they don't the call to this method has no effect.

        :param component: the component to unset references.
        """
        if isinstance(component, IUnreferenceable):
            component.unset_references()

    @staticmethod
    def unset_references(components: List[Any]):
        """
        Unsets references in multiple components.

        To unset references components must implement :class:`IUnreferenceable <pip_services3_commons.refer.IUnreferenceable.IUnreferenceable>` interface.
        If they don't the call to this method has no effect.

        :param components: the list of components, whose references must be cleared.
        """
        if components is None:
            return

        for component in components:
            Referencer.unset_references_for_one(component)
