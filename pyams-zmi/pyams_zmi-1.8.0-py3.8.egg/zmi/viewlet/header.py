#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zmi.zmi.viewlet.header module

This module provides the "pyams.page_header" viewlet manager, which is used to build the
top panel of PyAMS management interface.
"""

from zope.component import queryMultiAdapter
from zope.interface import Interface

from pyams_skin.interfaces.view import IModalPage
from pyams_skin.interfaces.viewlet import IHeaderViewletManager
from pyams_template.template import get_view_template, template_config
from pyams_utils.adapter import adapter_config
from pyams_viewlet.manager import TemplateBasedViewletManager, WeightOrderedViewletManager, \
    viewletmanager_config
from pyams_viewlet.viewlet import EmptyContentProvider, Viewlet, viewlet_config
from pyams_zmi.interfaces import IAdminLayer, IAdminView, IPageTitle
from pyams_zmi.interfaces.configuration import IZMIConfiguration
from pyams_zmi.interfaces.viewlet import IPageHeaderViewletManager


__docformat__ = 'restructuredtext'

from pyams_zmi import _  # pylint: disable=ungrouped-imports


@viewletmanager_config(name='pyams.page_header', layer=IAdminLayer,
                       provides=IPageHeaderViewletManager)
@template_config(template='templates/page-header.pt')
class PageHeaderViewletManager(TemplateBasedViewletManager, WeightOrderedViewletManager):
    """Page header viewlet manager"""

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        configuration = IZMIConfiguration(request.root, None)
        if (configuration is None) or not configuration.include_header:
            return EmptyContentProvider.__new__(EmptyContentProvider)
        return WeightOrderedViewletManager.__new__(cls)


@viewlet_config(name='pyams.content_header', layer=IAdminLayer,
                manager=IHeaderViewletManager, weight=10)
@template_config(template='templates/header.pt')
@template_config(template='templates/modal-header.pt', name='modal')
class ContentHeaderViewlet(Viewlet):
    """Content header viewlet"""

    _title = _("PyAMS admin page")

    modal_template = get_view_template(name='modal')

    @property
    def title(self):
        """Title getter"""
        title = queryMultiAdapter((self.context, self.request, self.view), IPageTitle)
        return title or self._title

    def render(self):
        if IModalPage.providedBy(self.view):
            return self.modal_template()
        return super().render()


@adapter_config(required=(Interface, IAdminLayer, IAdminView),
                provides=IPageTitle)
def admin_view_title_adapter(context, request, view):  # pylint: disable=unused-argument
    """Admin view default title adapter"""
    configuration = IZMIConfiguration(request.root)
    return configuration.site_name
