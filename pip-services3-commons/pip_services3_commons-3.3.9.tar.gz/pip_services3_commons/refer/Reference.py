# -*- coding: utf-8 -*-
"""
    pip_services3_commons.refer.Reference
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Reference component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any


class Reference(object):
    """
    Contains a reference to a component and locator to find it.
    It is used by :class:`References <pip_services3_commons.refer.References.References>` to store registered component references.
    """

    def __init__(self, locator: Any, component: Any):
        """
        Create a new instance of the reference object and assigns its values.

        :param locator: a locator to find the reference.

        :param component: a reference to component.
        """
        if component is None:
            raise Exception("Component cannot be null")

        self.__locator: Any = locator
        self.__component: Any = component

    def match(self, locator: Any) -> bool:
        """
        Matches locator to this reference locator. Descriptors are matched using equal method.
        All obj locator types are matched using direct comparison.

        :param locator: the locator to match.

        :return: true if locators are matching and false it they don't.
        """
        # Locate by direct reference matching
        if self.__component == locator:
            return True
        # Locate by direct locator matching
        elif not (self.__locator is None):
            return self.__locator == locator
        else:
            return False

    def get_component(self) -> Any:
        """
        Gets the stored component reference.

        :return: the component's references.
        """
        return self.__component

    def get_locator(self) -> Any:
        """
        Gets the stored component locator.

        :return: the component's locator.
        """
        return self.__locator
