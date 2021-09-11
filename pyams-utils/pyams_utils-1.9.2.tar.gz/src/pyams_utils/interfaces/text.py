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

"""PyAMS_utils.interfaces.text module

This module provides a single interface used by HTML rendering adapters, which are used to convert
any object to an HTML representation.
"""

from zope.interface import Attribute, Interface


__docformat__ = 'restructuredtext'

from pyams_utils import _


class IHTMLRenderer(Interface):
    """Text renderer interface

    HTML renderers are implemented as adapters for a source object (which can
    be a string) and a request, so that you can easily implement custom renderers
    for any object and/or for any request layer.
    """

    label = Attribute(_("Optional renderer label"))

    def render(self, **kwargs):
        """Render adapted text"""
