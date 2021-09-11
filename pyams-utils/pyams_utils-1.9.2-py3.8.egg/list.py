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

"""PyAMS_utils list module

This module is dedicated to lists and iterators management. It provides function to extract
unique values from a list or iterator in their original order, or to iterate over an iterator in
random order; it also provides a "boolean_iter" function (usable as TALES extension) to check if
an iterator returns at least one value, without consuming this iterator (the function returns a
tuple containing a boolean value to specify if iterator is empty or not, and the original
iterator).
"""

from itertools import filterfalse, tee
from random import random, shuffle

from zope.interface import Interface

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


def unique(seq, key=None):
    """Extract unique values from list, preserving order

    :param iterator seq: input list
    :param callable key: an identity function which is used to get 'identity' value of each element
        in the list
    :return: list; a new list containing only unique elements of the original list in their initial
        order. Original list is not modified.
    """
    seen = set()
    seen_add = seen.add
    result = []
    if key is None:
        for element in filterfalse(seen.__contains__, seq):
            seen_add(element)
            result.append(element)
    else:
        for element in seq:
            k = key(element)
            if k not in seen:
                seen_add(k)
                result.append(element)
    return result


def unique_iter(iterable, key=None):
    """Iterate over iterator values, yielding only unique values

    :param iterator iterable: input iterator
    :param callable key: an identity function which is used to get 'identity' value of each element
        in the list
    :return: an iterator of unique values
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def random_iter(iterable, limit=1):
    """Get items randomly from an iterator
    """
    selected = [None] * limit
    for index, item in enumerate(iterable):
        if index < limit:
            selected[index] = item
        else:
            selected_index = int(random() * (index+1))
            if selected_index < limit:
                selected[selected_index] = item
    shuffle(selected)
    return iter(selected)


def boolean_iter(iterable):
    """Check if an iterable returns at least one value, without consuming it.

    The function returns a tuple containing a boolean flag indicating if the original iterator
    is empty or not, and the original un-consumed iterator.
    """

    def inner_check():
        check, items = tee(iterable)
        try:
            next(check)
        except StopIteration:
            yield False
        else:
            yield True
            yield from items

    values = inner_check()
    return next(values), values


@adapter_config(name='boolean_iter',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class BooleanIterCheckerExpression(ContextRequestViewAdapter):
    """TALES expression used to handle iterators

    The expression returns a tuple containing a boolean flag indicating if the original iterator
    is empty or not, and the original un-consumed iterator.
    """

    def render(self, context=None):
        """Render TALES extension; see `ITALESExtension` interface"""
        if context is None:
            context = self.context
        return boolean_iter(context)
