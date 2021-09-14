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

"""PyAMS_thesaurus.extension.html module

This module defines thesaurus term HTML extension.
"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from pyams_thesaurus.extension.html.interfaces import IThesaurusTermHTMLInfo, \
    IThesaurusTermHTMLTarget, THESAURUS_TERM_HTML_INFO_KEY
from pyams_thesaurus.interfaces.extension import IThesaurusTermExtension
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


@factory_config(provided=IThesaurusTermHTMLInfo)
class ThesaurusTermHTMLInfo(Persistent, Contained):
    """Thesaurus term HTML description"""

    description = FieldProperty(IThesaurusTermHTMLInfo['description'])


@adapter_config(required=IThesaurusTermHTMLTarget,
                provides=IThesaurusTermHTMLInfo)
def thesaurus_term_html_description_factory(context):
    """Thesaurus term HTML description factory"""
    return get_annotation_adapter(context, THESAURUS_TERM_HTML_INFO_KEY, IThesaurusTermHTMLInfo)


@utility_config(name='html', provides=IThesaurusTermExtension)
class HTMLThesaurusExtension:
    """HTML description thesaurus extension"""

    label = _("Rich text description")
    weight = 10

    target_interface = IThesaurusTermHTMLTarget
    target_view = 'html-description.html'

    icon_css_class = 'fas fa-font'
