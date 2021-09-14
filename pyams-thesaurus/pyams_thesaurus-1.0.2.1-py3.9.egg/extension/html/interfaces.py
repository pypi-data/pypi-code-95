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

"""PyAMS_thesaurus.extension.html.interfaces module

This module defines interface of an HTML term extension, which allows to provide
a rich text content on any term.
"""

from zope.annotation import IAttributeAnnotatable
from zope.interface import Interface

from pyams_i18n.schema import I18nHTMLField


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _


THESAURUS_TERM_HTML_INFO_KEY = 'pyams_thesaurus.extension.html'


class IThesaurusTermHTMLInfo(Interface):
    """Thesaurus term HTML info"""

    description = I18nHTMLField(title=_("HTML content"),
                                required=False)


class IThesaurusTermHTMLTarget(IAttributeAnnotatable):
    """Thesaurus term HTML description target"""
