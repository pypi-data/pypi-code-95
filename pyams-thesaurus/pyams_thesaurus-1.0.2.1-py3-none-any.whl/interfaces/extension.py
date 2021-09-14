#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.interfaces.extension module

This module defines thesaurus interfaces related to extensions management, which
are utilities which can be used to add additional information to thesaurus terms.
"""

from zope.interface import Attribute, Interface
from zope.schema import TextLine, URI


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _


THESAURUS_EXTENSIONS_VOCABULARY = 'pyams_thesaurus.extensions'


class IThesaurusTermExtension(Interface):
    """Thesaurus term extension interface

    An extension is a marker interface implemented by
    a term, which provides additional attributes to the term.

    Each available extension is defined as a named utility.
    """

    label = TextLine(title=_("Extension name"),
                     description=_("User name given to the extension"),
                     required=True)

    target_interface = Attribute(_("Extension marker interface"))

    target_view = URI(title=_("Extension target view name"),
                      required=True)

    icon_css_class = TextLine(title=_("Extension icon CSS class"),
                              required=True)
