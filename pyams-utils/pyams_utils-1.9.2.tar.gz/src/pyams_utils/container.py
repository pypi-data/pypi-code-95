#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
# pylint: disable=no-name-in-module

"""PyAMS_utils.container module

This module provides several classes, adapters and functions about containers.
"""

from BTrees.OOBTree import OOBTree  # pylint: disable=import-error
from persistent.list import PersistentList
from pyramid.threadlocal import get_current_registry
from zope.container.interfaces import IContained, IContainer
from zope.container.ordered import OrderedContainer
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.location.interfaces import ISublocations

from pyams_utils.adapter import ContextAdapter, adapter_config


__docformat__ = 'restructuredtext'


class SimpleContainerMixin:
    """Simple container mixin class"""

    next_id = 1

    def append(self, obj):
        """Append object to container"""
        key = str(self.next_id)
        self[key] = obj
        self.next_id += 1
        return obj.__name__


class BTreeOrderedContainer(OrderedContainer):
    """BTree based ordered container

    This container maintain a manual order of it's contents
    """

    def __init__(self):
        # pylint: disable=super-init-not-called
        self._data = OOBTree()
        self._order = PersistentList()


class ParentSelector:
    """Interface based parent selector

    This selector can be used as a subscriber predicate on IObjectAddedEvent to define
    an interface that the new parent must support for the event to be applied:

    .. code-block:: python

        from pyams_utils.interfaces.site import ISiteRoot

        @subscriber(IObjectAddedEvent, parent_selector=ISiteRoot)
        def siteroot_object_added_event_handler(event):
            '''This is an event handler for an ISiteRoot object added event'''
    """

    def __init__(self, ifaces, config):
        # pylint: disable=unused-argument
        if not isinstance(ifaces, (list, tuple, set)):
            ifaces = (ifaces,)
        self.interfaces = ifaces

    def text(self):
        """Predicate string output"""
        return 'parent_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event):
        if not IObjectMovedEvent.providedBy(event):
            return False
        for intf in self.interfaces:
            try:
                if intf.providedBy(event.newParent):
                    return True
            except (AttributeError, TypeError):
                if isinstance(event.newParent, intf):
                    return True
        return False


@adapter_config(required=IContained, provides=ISublocations)
class ContainerSublocationsAdapter(ContextAdapter):
    """Contained object sub-locations adapter

    This adapter checks for custom ISublocations interface adapters which can
    be defined by any component to get access to inner locations, defined for
    example via annotations.
    """

    def sublocations(self):
        """See `zope.location.interfaces.ISublocations` interface"""
        context = self.context
        # Check for adapted sub-locations first...
        registry = get_current_registry()
        for name, adapter in registry.getAdapters((context,), ISublocations):
            if not name:  # don't reuse default adapter!!
                continue
            yield from adapter.sublocations()
        # then yield container items
        if IContainer.providedBy(context):
            yield from context.values()


def find_objects_matching(root, condition, ignore_root=False):
    """Find all objects in root that match the condition

    The condition is a Python callable object that takes an object as
    argument and must return a boolean result.

    All sub-objects of the root will also be searched recursively.

    :param object root: the parent object from which search is started
    :param callable condition: a callable object which may return true for a given
        object to be selected
    :param boolean ignore_root: if *True*, the root object will not be returned, even if it matches
        the given condition
    :return: an iterator for all root's sub-objects matching condition
    """
    if (not ignore_root) and condition(root):
        yield root
    locations = ISublocations(root, None)
    if locations is not None:
        for location in locations.sublocations():  # pylint: disable=too-many-function-args
            if condition(location):
                yield location
            yield from find_objects_matching(location, condition, ignore_root=True)


def find_objects_providing(root, interface, ignore_root=False):
    """Find all objects in root that provide the specified interface

    All sub-objects of the root will also be searched recursively.

    :param object root: object; the parent object from which search is started
    :param Interface interface: interface; an interface that sub-objects should provide
    :param boolean ignore_root: if *True*, the root object will not be returned, even if it
        provides the given interface
    :return: an iterator for all root's sub-objects that provide the given interface
    """
    yield from find_objects_matching(root, interface.providedBy, ignore_root)
