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

"""PyAMS_thesaurus.zmi.thesaurus module

This module provides main thesaurus management components.
"""

from pyramid.events import subscriber
from zope.copy import copy
from zope.interface import Interface, Invalid, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IAddForm, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import MANAGE_SYSTEM_PERMISSION, VIEW_SYSTEM_PERMISSION
from pyams_skin.interfaces.viewlet import IBreadcrumbItem
from pyams_skin.viewlet.actions import ContextAction
from pyams_table.interfaces import IColumn
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusInfo, IThesaurusManager
from pyams_thesaurus.zmi import ThesaurusListTable
from pyams_thesaurus.zmi.interfaces import IThesaurusTermsTreeMenu
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import query_utility
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, AdminModalAddForm
from pyams_zmi.helper.event import get_json_table_row_add_callback, \
    get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import ActionColumn, TableElementEditor
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.breadcrumb import AdminLayerBreadcrumbItem
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


class IThesaurusAddForm(IAddForm):
    """Thesaurus add form marker interface"""


@subscriber(IDataExtractedEvent, form_selector=IThesaurusAddForm)
def handle_new_thesaurus_data_extraction(event):
    """Handle new thesaurus data"""
    name = event.data['name'] or ''
    thesaurus = query_utility(IThesaurus, name=name)
    if thesaurus is not None:
        event.form.widgets.errors += (Invalid(_("Another thesaurus is already "
                                                "registered with this name!")),)


@implementer(IThesaurusAddForm)
class ThesaurusAddFormMixin:
    """Thesaurus add form mixin"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return '<small>{}</small><br />{}'.format(
            get_object_label(self.context, self.request, self),
            translate(_("New thesaurus")))


@adapter_config(required=(IThesaurusManager, IAdminLayer, IThesaurusAddForm),
                provides=IAJAXFormRenderer)
class ThesaurusAddFormRenderer(ContextRequestViewAdapter):
    """Thesaurus add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        manager = get_parent(self.context, IThesaurusManager)
        return {
            'callbacks': [
                get_json_table_row_add_callback(manager, self.request,
                                                ThesaurusListTable, changes)
            ]
        }


#
# Thesaurus add form
#

@viewlet_config(name='add-thesaurus.menu',
                context=IThesaurusManager, layer=IAdminLayer, view=ThesaurusListTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusAddMenu(ContextAction):
    """Thesaurus add menu"""

    status = 'success'
    icon_class = 'fas fa-plus'
    label = _("Add thesaurus")

    href = 'add-thesaurus.html'
    modal_target = True


@ajax_form_config(name='add-thesaurus.html',
                  context=IThesaurusManager, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusAddForm(ThesaurusAddFormMixin, AdminModalAddForm):
    """Thesaurus add form"""

    legend = _("New thesaurus properties")

    fields = Fields(IThesaurusInfo).select('name', 'title', 'subject', 'description',
                                           'language', 'creator', 'publisher', 'created')
    content_factory = IThesaurus

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context[oid] = obj


#
# Thesaurus clone form
#

@adapter_config(name='clone',
                required=(IThesaurusManager, IAdminLayer, ThesaurusListTable),
                provides=IColumn)
class ThesaurusCloneColumn(ActionColumn):
    """Thesaurus clone column"""

    hint = _("Clone thesaurus")
    icon_class = 'far fa-clone'

    href = 'clone-thesaurus.html'

    permission = MANAGE_SYSTEM_PERMISSION
    weight = 100


@ajax_form_config(name='clone-thesaurus.html',
                  context=IThesaurus, layer=IPyAMSLayer,
                  permission=MANAGE_SYSTEM_PERMISSION)
class ThesaurusCloneForm(ThesaurusAddFormMixin, AdminModalAddForm):
    """Thesaurus clone form"""

    legend = _("Clone thesaurus")

    fields = Fields(IThesaurusInfo).select('name')

    def create(self, data):
        return copy(self.context)

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context.__parent__[oid] = obj


#
# Thesaurus editor components
#

@adapter_config(required=(IThesaurus, IAdminLayer, Interface),
                provides=ITableElementEditor)
class ThesaurusElementEditor(TableElementEditor):
    """Thesaurus table element editor"""

    view_name = 'admin'
    modal_target = False


@adapter_config(required=(IThesaurus, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class ThesaurusBreadcrumbItem(AdminLayerBreadcrumbItem):
    """Thesaurus breadcrumb item"""

    @property
    def label(self):
        """Breadcrumb label getter"""
        return self.context.name


@viewlet_config(name='properties.menu',
                context=IThesaurus, layer=IAdminLayer,
                manager=IThesaurusTermsTreeMenu, weight=10,
                permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusPropertiesMenu(NavigationMenuItem):
    """Thesaurus properties menu"""

    label = _("Properties")
    href = '#properties.html'


@ajax_form_config(name='properties.html',
                  context=IThesaurus, layer=IPyAMSLayer)
class ThesaurusEditForm(AdminEditForm):
    """Thesaurus edit form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return translate(_("Thesaurus: {}")).format(self.context.name)

    legend = _("Thesaurus properties")

    fields = Fields(IThesaurusInfo).select('name', 'title', 'subject', 'description',
                                           'language', 'creator', 'publisher', 'created')

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        name = self.widgets.get('name')
        if name is not None:
            name.mode = DISPLAY_MODE


@adapter_config(required=(IThesaurus, IAdminLayer, ThesaurusEditForm),
                provides=IAJAXFormRenderer)
class ThesaurusEditFormAJAXRenderer(ContextRequestViewAdapter):
    """Thesaurus edit form AJAX renderer"""

    def render(self, changes):
        """AJAX result renderer"""
        if not changes:
            return None
        manager = get_parent(self.context, IThesaurusManager)
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(manager, self.request,
                                                    ThesaurusListTable, self.context)
            ]
        }
