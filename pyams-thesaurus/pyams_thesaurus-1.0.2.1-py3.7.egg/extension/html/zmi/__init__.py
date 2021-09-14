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

"""PyAMS_thesaurus.extension.html.zmi module

This module defines management components of thesaurus term HTML extension.
"""

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_thesaurus.extension.html import IThesaurusTermHTMLInfo, IThesaurusTermHTMLTarget
from pyams_thesaurus.zmi.extension import ThesaurusTermExtensionEditForm


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _


@ajax_form_config(name='html-description.html',
                  context=IThesaurusTermHTMLTarget, layer=IPyAMSLayer,
                  permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusTermHTMLDescriptionEditForm(ThesaurusTermExtensionEditForm):
    """Thesaurus term HTML description edit form"""

    legend = _("HTML description")
    modal_class = 'modal-xl'

    fields = Fields(IThesaurusTermHTMLInfo)

    def get_content(self):
        return IThesaurusTermHTMLInfo(self.context)
