# -*- coding: utf-8 -*-
"""
    pip_services3_commons.refer.IReferences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for references components.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Any, List




class IReferences(ABC):
    """
    Interface for a map that holds component references and passes them to components
    to establish dependencies with each obj.

    Together with :class:`IReferenceable <pip_services3_commons.refer.IReferenceable.IReferenceable>` and :class:`IUnreferenceable <pip_services3_commons.refer.IUnreferenceable.IUnreferenceable>` interfaces it implements
    a Locator pattern that is used by PipServices toolkit for Inversion of Control
    to assign external dependencies to components.

    The IReferences object is a simple map, where keys are locators
    and values are component references. It allows to add, remove and find components
    by their locators. Locators can be any values like integers, strings or component types.
    But most often PipServices toolkit uses :class:`Descriptor <pip_services3_commons.refer.Descriptor.Descriptor>` as locators that match
    by 5 fields: group, type, kind, name and version.

    Example:

    .. code-block:: python

        class MyController(IReferences):
            _persistence = None

            def set_references(self, references):
                self._persistence = references.get_one_required(Descriptor("mygroup", "persistence", "*", "*", "1.0"))

        persistence = MyMongoDbPersistence()

        references = References.from_tuples(
        Descriptor("mygroup", "persistence", "mongodb", "default", "1.0"), persistence,
        Descriptor("mygroup", "controller", "default", "default", "1.0"), controller)

        controller.set_references(references)
    """

    def put(self, locator: Any = None, reference: Any = None):
        """
        Puts a new reference into this reference map.

        :param locator: a component reference to be added.

        :param reference: a locator to find the reference by.
        """
        raise NotImplementedError('Method from interface definition')

    def remove(self, locator: Any) -> Any:
        """
        Removes a previously added reference that matches specified locator.
        If many references match the locator, it removes only the first one.
        When all references shall be removed, use :func:remove_all method instead.

        :param locator: a locator to remove reference

        :return: the removed component reference.
        """
        raise NotImplementedError('Method from interface definition')

    def remove_all(self, locator: Any) -> List[Any]:
        """
        Removes all component references that match the specified locator.

        :param locator: a locator to remove reference
        :return: a list, containing all removed references.
        """
        raise NotImplementedError('Method from interface definition')

    def get_all_locators(self) -> List[Any]:
        """
        Gets locators for all registered component references in this reference map.

        :return: a list with component locators.
        """
        raise NotImplementedError('Method from interface definition')

    def get_all(self) -> List[Any]:
        """
        Gets all component references registered in this reference map.

        :return: a list with component references.
        """
        raise NotImplementedError('Method from interface definition')

    def get_optional(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find references by.

        :return: a list with matching component references or empty list if nothing was found.
        """
        raise NotImplementedError('Method from interface definition')

    def get_required(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.
        At least one component reference must be present. If it doesn't the method throws an error.

        :param locator: the locator to find references by.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
        """
        raise NotImplementedError('Method from interface definition')

    def get_one_optional(self, locator: Any) -> Any:
        """
        Gets an optional component reference that matches specified locator.

        :param locator: the locator to find references by.

        :return: a matching component reference or null if nothing was found.
        """
        raise NotImplementedError('Method from interface definition')

    def get_one_required(self, locator: Any) -> Any:
        """
        Gets a __required component reference that matches specified locator.

        :param locator: the locator to find a reference by.

        :return: a matching component reference.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
        """
        raise NotImplementedError('Method from interface definition')

    def get_one_before(self, reference, locator):
        raise NotImplementedError('Method from interface definition')

    def find(self, locator: Any, required: bool) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find a reference by.

        :param required: forces to raise an error if no reference is found.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when __required is set to true but no references found.
        """
        raise NotImplementedError('Method from interface definition')
