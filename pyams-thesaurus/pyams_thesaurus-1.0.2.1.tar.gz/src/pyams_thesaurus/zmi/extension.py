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

"""PyAMS_thesaurus.zmi.extension module

This module defines base components for extensions management.
"""
from pyams_thesaurus.interfaces import MANAGE_THESAURUS_CONTENT_PERMISSION
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_utils.traversing import get_parent
from pyams_zmi.form import AdminModalEditForm


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


class ThesaurusTermExtensionEditForm(AdminModalEditForm):
    """Thesaurus term extension properties edit form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        thesaurus = get_parent(self.context, IThesaurus)
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(thesaurus.name),
            translate(_("Term: {}")).format(self.context.label))

    _edit_permission = MANAGE_THESAURUS_CONTENT_PERMISSION
