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

"""PyAMS_thesaurus.zmi main module

This module defines main ZMI components used to manage thesaurus.
"""

from fanstatic import Library, Resource
from pyramid.view import view_config
from zope.interface import Interface

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION, VIEW_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.viewlet import IBreadcrumbItem
from pyams_table.interfaces import IColumn, IValues
from pyams_thesaurus.interfaces.thesaurus import IThesaurusManager
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.fanstatic import ExternalResource
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IControlPanelMenu, IMenuHeader, IPropertiesMenu, \
    ISiteManagementMenu
from pyams_zmi.table import NameColumn, Table, TableAdminView, TableElementEditor, TrashColumn
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.breadcrumb import AdminLayerBreadcrumbItem
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


#
# Fanstatic resources
#

library = Library('pyams_thesaurus', 'resources')

thesaurus_css = Resource(library, 'css/thesaurus.css',
                         minified='css/thesaurus.min.css')

thesaurus_js = Resource(library, 'js/thesaurus.js',
                        minified='js/thesaurus.min.js')


#
# Thesaurus manager management components
#

THESAURUS_MANAGER_LABEL = _("Thesaurus container")


@viewlet_config(name='thesaurus-manager.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IControlPanelMenu, weight=30,
                permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusManagerMenu(NavigationMenuItem):
    """Thesaurus manager menu"""

    label = _("Thesaurus")
    icon_class = 'fas fa-language'

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        manager = query_utility(IThesaurusManager)
        if (manager is None) or not manager.root_menu:
            return None
        return NavigationMenuItem.__new__(cls)

    def get_href(self):
        """Menu URL getter"""
        manager = get_utility(IThesaurusManager)
        return absolute_url(manager, self.request, 'admin')


@adapter_config(required=(IThesaurusManager, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class ThesaurusManagerBreadcrumbItem(AdminLayerBreadcrumbItem):
    """Thesaurus manager breadcrumb item"""

    label = THESAURUS_MANAGER_LABEL


@adapter_config(required=(IThesaurusManager, IPyAMSLayer, Interface),
                provides=IObjectLabel)
def thesaurus_manager_label(context, request, view):  # pylint: disable=unused-argument
    """Thesaurus manager label"""
    return request.localizer.translate(THESAURUS_MANAGER_LABEL)


@adapter_config(required=(IThesaurusManager, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def thesaurus_manager_menu_header(context, request, view, manager):  # pylint: disable=unused-argument
    """Thesaurus manager menu header"""
    return THESAURUS_MANAGER_LABEL


@adapter_config(required=(IThesaurusManager, IAdminLayer, Interface),
                provides=ITableElementEditor)
class ThesaurusManagerElementEditor(TableElementEditor):
    """Thesaurus manager element editor"""

    view_name = 'admin#thesaurus-list.html'
    modal_target = False


@viewletmanager_config(name='thesaurus-list.menu',
                       context=IThesaurusManager, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=10,
                       permission=VIEW_SYSTEM_PERMISSION,
                       provides=IPropertiesMenu)
class ThesaurusListMenu(NavigationMenuItem):
    """Thesaurus list menu"""

    label = _("Thesaurus list")
    icon_class = 'fas fa-language'
    href = '#thesaurus-list.html'


class ThesaurusListTable(Table):
    """Thesaurus list table"""

    display_if_empty = True


@adapter_config(required=(IThesaurusManager, IAdminLayer, ThesaurusListTable),
                provides=IValues)
class ThesaurusListTableValues(ContextRequestViewAdapter):
    """Thesaurus manager table values adapter"""

    @property
    def values(self):
        """SQLAlchemy manager table values getter"""
        yield from self.context.values()


@adapter_config(name='name',
                required=(IThesaurusManager, IAdminLayer, ThesaurusListTable),
                provides=IColumn)
class ThesaurusManagerNameColumn(NameColumn):
    """Thesaurus manager name column"""


@adapter_config(name='trash',
                required=(IThesaurusManager, IAdminLayer, ThesaurusListTable),
                provides=IColumn)
class ThesaurusManagerTrashColumn(TrashColumn):
    """Thesaurus manager trash column"""

    permission = MANAGE_SYSTEM_PERMISSION


@pagelet_config(name='thesaurus-list.html',
                context=IThesaurusManager, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusListView(TableAdminView):
    """Thesaurus manager list view"""

    title = _("Thesaurus list")
    table_class = ThesaurusListTable
    table_label = _("List of thesaurus")

    @property
    def back_url(self):
        """Form back URL getter"""
        return absolute_url(self.request.root, self.request, 'admin#utilities.html')  # pylint: disable=no-member

    back_url_target = None


@view_config(name='delete-element.json',
             context=IThesaurusManager, request_type=IPyAMSLayer,
             permission=MANAGE_SYSTEM_PERMISSION, renderer='json', xhr=True)
def delete_thesaurus(request):
    """Delete thesaurus"""
    return delete_container_element(request)


#
# Thesaurus manager properties edit form
#

@viewlet_config(name='properties.menu',
                context=IThesaurusManager, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=10,
                permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusManagerPropertiesMenu(NavigationMenuItem):
    """Thesaurus manager properties menu"""

    label = _("Properties")
    href = '#properties.html'
    modal_target = False


@ajax_form_config(name='properties.html',
                  context=IThesaurusManager, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusManagerPropertiesEditForm(AdminEditForm):
    """Thesaurus manager properties edit form"""

    @property
    def title(self):
        """Title getter"""
        return get_object_label(self.context, request=self.request)

    legend = _("Thesaurus manager properties")

    fields = Fields(IThesaurusManager).omit('__name__', '__parent__')

    label_css_class = 'control-label col-md-1'
