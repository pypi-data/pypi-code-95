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

"""PyAMS_thesaurus.zmi.interfaces module

This module defines thesaurus management components interfaces.
"""

from zope.interface import Interface
from zope.schema import TextLine

from pyams_form.interfaces import INPUT_MODE
from pyams_form.template import widget_template_config
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.widget import IDynamicSelectWidget


__docformat__ = 'restructuredtext'


class IThesaurusTermsTreeMenu(Interface):
    """Thesaurus terms tree menu marker interface"""


class IThesaurusTermWidget(IDynamicSelectWidget):
    """Single term widget"""

    thesaurus_name = TextLine(title="Thesaurus name",
                              required=False)

    extract_name = TextLine(title="Extract name",
                            required=False)


class IThesaurusTermsListWidget(IDynamicSelectWidget):
    """Terms list widget"""

    thesaurus_name = TextLine(title="Thesaurus name",
                              required=False,
                              default='')

    extract_name = TextLine(title="Extract name",
                            required=False,
                            default='')


@widget_template_config(mode=INPUT_MODE,
                        layer=IPyAMSLayer,
                        template='templates/widget/terms-tree-input.pt')
class IThesaurusTermsTreeWidget(IThesaurusTermsListWidget):
    """Terms tree widget"""
