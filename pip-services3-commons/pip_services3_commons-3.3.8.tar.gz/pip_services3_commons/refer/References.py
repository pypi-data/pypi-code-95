# -*- coding: utf-8 -*-
"""
    pip_services3_commons.refer.References
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Referencescomponent implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading
from typing import List, Any, Sequence

from .IReferences import IReferences
from .Reference import Reference
from .ReferenceException import ReferenceException




class References(IReferences):
    """
    The most basic implementation of :class:`IReferences <pip_services3_commons.refer.IReferences.IReferences>` to store and locate component references.

    Example:

    .. code-block:: python

        class MyController(IReferenceable):
            _persistence = None

            def set_references(self, references):
                self._persistence = references.getOneRequired(Descriptor("mygroup", "persistence", "*", "*", "1.0"))

        persistence = MyMongoDbPersistence()

        references = References.from_tuples(
        Descriptor("mygroup", "persistence", "mongodb", "default", "1.0"), persistence,
        Descriptor("mygroup", "controller", "default", "default", "1.0"), controller)

        controller.set_references(references)


    """

    __lock = None

    def __init__(self, tuples: Sequence[Any] = None):
        """
        Creates a new instance of references and initializes it with references.

        :param tuples: (optional) a list of values where odd elements are locators
        and the following even elements are component references
        """
        self._references: List[Reference] = []
        self.__lock = threading.Lock()

        if not (tuples is None):
            index = 0
            while index < len(tuples):
                if index + 1 >= len(tuples):
                    break
                self.put(tuples[index], tuples[index + 1])
                index = index + 2

    def put(self, locator: Any = None, component: Any = None):
        """
        Puts a new reference into this reference map.

        :param locator: a component reference to be added.

        :param component: a locator to find the reference by.
        """
        if component is None:
            raise Exception("Component cannot be null")

        self.__lock.acquire()
        try:
            self._references.append(Reference(locator, component))
        finally:
            self.__lock.release()

    def remove(self, locator: Any) -> Any:
        """
        Removes a previously added reference that matches specified locator.
        If many references match the locator, it removes only the first one.
        When all references shall be removed, use :func:`remove_all` method instead.

        :param locator: a locator to remove reference

        :return: the removed component reference.
        """
        if locator is None:
            return None

        self.__lock.acquire()
        try:
            for reference in reversed(self._references):
                if reference.match(locator):
                    self._references.remove(reference)
                    return reference.get_component()
        finally:
            self.__lock.release()

        return None

    def remove_all(self, locator: Any) -> List[Any]:
        """
        Removes all component references that match the specified locator.

        :param locator: a locator to remove reference by.

        :return: a list, containing all removed references.
        """
        components = []

        if locator is None:
            return components

        self.__lock.acquire()
        try:
            for reference in reversed(self._references):
                if reference.match(locator):
                    self._references.remove(reference)
                    components.append(reference.get_component())
        finally:
            self.__lock.release()

        return components

    def get_all_locators(self) -> List[Any]:
        """
        Gets locators for all registered component references in this reference map.

        :return: a list with component locators.
        """
        locators = []

        self.__lock.acquire()
        try:
            for reference in self._references:
                locators.append(reference.get_locator())
        finally:
            self.__lock.release()

        return locators

    def get_all(self) -> List[Any]:
        """
        Gets all component references registered in this reference map.

        :return: a list with component references.
        """
        components = []

        self.__lock.acquire()
        try:
            for reference in self._references:
                components.append(reference.get_component())
        finally:
            self.__lock.release()

        return components

    def get_optional(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find references by.

        :return: a list with matching component references or empty list if nothing was found.
        """
        try:
            return self.find(locator, False)
        except Exception as ex:
            return []

    def get_required(self, locator: Any) -> List[Any]:
        """
        Gets all component references that match specified locator.
        At least one component reference must be present. If it doesn't the method throws an error.

        :param locator: the locator to find references by.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
        """
        return self.find(locator, True)

    def get_one_optional(self, locator: Any) -> Any:
        """
        Gets an optional component reference that matches specified locator.

        :param locator: the locator to find references by.

        :return: a matching component reference or null if nothing was found.
        """
        try:
            components = self.find(locator, False)
            return components[0] if len(components) > 0 else None
        except Exception as ex:
            return None

    def get_one_required(self, locator: Any) -> Any:
        """
         Gets a __required component reference that matches specified locator.

         :param locator: the locator to find a reference by.

         :return: a matching component reference.

         :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when no references found.
         """
        components = self.find(locator, True)
        return components[0] if len(components) > 0 else None

    def find(self, locator: Any, required: bool) -> List[Any]:
        """
        Gets all component references that match specified locator.

        :param locator: the locator to find a reference by.

        :param required: forces to raise an error if no reference is found.

        :return: a list with matching component references.

        :raises: a :class:`ReferenceException <pip_services3_commons.refer.ReferenceException.ReferenceException>` when __required is set to true but no references found.
        """
        if locator is None:
            raise Exception("Locator cannot be null")

        components = []

        self.__lock.acquire()
        try:
            index = len(self._references) - 1

            while index >= 0:
                reference = self._references[index]
                if reference.match(locator):
                    component = reference.get_component()
                    components.append(component)
                index = index - 1

            if len(components) == 0 and required:
                raise ReferenceException(None, locator)
        finally:
            self.__lock.release()

        return components

    @staticmethod
    def from_tuples(*tuples: Any) -> 'References':
        """
        Creates a new References from a list of key-args pairs called tuples.

        :param tuples: a list of values where odd elements are locators
                      and the following even elements are component references

        :return: a newly created References.
        """
        return References(tuples)
