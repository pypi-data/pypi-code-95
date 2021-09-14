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

"""PyAMS_thesaurus.zmi.extract module

This module provides extracts management components.
"""

from html import unescape

from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from zope.copy import copy
from zope.interface import Interface, Invalid, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.group import Group
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IAddForm, IDataExtractedEvent, \
    IInnerSubForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_skin.interfaces.viewlet import IContentSuffixViewletManager
from pyams_skin.viewlet.actions import ContextAction
from pyams_table.interfaces import IColumn, IValues
from pyams_template.template import template_config
from pyams_thesaurus.interfaces import ADMIN_THESAURUS_PERMISSION, \
    MANAGE_THESAURUS_EXTRACT_PERMISSION
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtract, \
    IThesaurusExtractInfo, IThesaurusExtractRoles, IThesaurusExtracts, IThesaurusManager
from pyams_thesaurus.zmi.tree import ThesaurusTermsView
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tree import INode, ITree
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import ViewContentProvider, Viewlet, viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalDisplayForm, AdminModalEditForm
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.helper.event import get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer, ICompositeView
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import ActionColumn, JsActionColumn, NameColumn, Table, TableElementEditor, \
    TableView, TrashColumn
from pyams_zmi.utils import get_object_label


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


#
# Thesaurus extracts table
#

class ThesaurusExtractsTable(Table):
    """Thesaurus extracts view"""

    css_classes = {
        'table': 'table table-striped table-hover table-sm datatable extracts'
    }

    @property
    def data_attributes(self):
        attributes = super().data_attributes
        attributes['table'].update({
            'data-ams-order': '1,asc'
        })
        return attributes

    display_if_empty = True


@adapter_config(required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IValues)
class ThesaurusExtractsValues(ContextRequestViewAdapter):
    """Thesaurus extracts table values"""

    @property
    def values(self):
        """Extracts table values getter"""
        yield from IThesaurusExtracts(self.context).values()


@adapter_config(name='thesaurus-extracts.view',
                required=(IThesaurus, IAdminLayer, ThesaurusTermsView),
                provides=ICompositeView)
class ThesaurusExtractsView(TableView, ViewContentProvider):
    """Thesaurus extracts view"""

    table_class = ThesaurusExtractsTable
    table_label = _("Thesaurus extracts")

    weight = 10

    @property
    def back_url(self):
        """Form back URL getter"""
        manager = get_utility(IThesaurusManager)
        return absolute_url(manager, self.request, 'admin#thesaurus-list.html')

    back_url_target = None


@adapter_config(name='tree',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractTreeColumn(ActionColumn):
    """Thesaurus extract tree column"""

    hint = _("Display extract terms")
    icon_class = 'fas fa-stream'

    href = 'terms-view.html'
    weight = 1


@adapter_config(name='name',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractNameColumn(NameColumn):
    """Thesaurus extract name column"""


@adapter_config(name='color',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractColorColumn(ActionColumn):
    """Thesaurus extract color column"""

    weight = 40

    def render_cell(self, item):
        return '<i class="fas fa-fw fa-square" style="color: #{};"></i>'.format(item.color)


@adapter_config(name='switch',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractVisibleSwitchColumn(JsActionColumn):
    """Thesaurus extract visible switch column"""

    icon_class = 'far fa-eye switcher'
    hint = _("Show/hide extract")

    href = 'MyAMS.thesaurus.tree.switchExtract'
    modal_target = False

    weight = 50


@adapter_config(name='trash',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractTrashColumn(TrashColumn):
    """Thesaurus extract trash column"""

    object_data = {
        'ams-modules': 'container',
        'ams-delete-target': 'delete-extract.json'
    }

    permission = ADMIN_THESAURUS_PERMISSION


@view_config(name='delete-extract.json',
             context=IThesaurus, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=ADMIN_THESAURUS_PERMISSION)
def delete_thesaurus_extract(request):
    """Delete thesaurus extract"""
    return delete_container_element(request, IThesaurusExtracts)


#
# Thesaurus extracts add forms
#

class IThesaurusExtractAddForm(IAddForm):
    """Thesaurus extract add form marker interface"""


@subscriber(IDataExtractedEvent, form_selector=IThesaurusExtractAddForm)
def handle_new_thesaurus_extract_data_extraction(event):
    """Handle new thesaurus extract data"""
    name = event.data['name']
    thesaurus = get_parent(event.form.context, IThesaurus)
    extracts = IThesaurusExtracts(thesaurus)
    if name in extracts:
        event.form.widgets.errors += (Invalid(_("Another extract is already "
                                                "registered with this name!")),)


@adapter_config(required=(IThesaurus, IAdminLayer, IThesaurusExtractAddForm),
                provides=IAJAXFormRenderer)
class ThesaurusExtractAddFormRenderer(ContextRequestViewAdapter):
    """Thesaurus extract add form AJAX renderer"""

    def render(self, changes):  # pylint: disable=no-self-use
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'status': 'reload'
        }


#
# Extract add form
#

@viewlet_config(name='add-extract.menu',
                context=IThesaurus, layer=IAdminLayer, view=ThesaurusExtractsTable,
                manager=IToolbarViewletManager, weight=10,
                permission=ADMIN_THESAURUS_PERMISSION)
class ThesaurusExtractAddMenu(ContextAction):
    """Thesaurus extract add menu"""

    status = 'success'
    icon_class = 'fas fa-plus'
    label = _("Add extract")

    href = 'add-extract.html'
    modal_target = True


@implementer(IThesaurusExtractAddForm)
class ThesaurusExtractAddFormMixin:
    """Thesaurus extract add form mixin"""

    @property
    def title(self):
        """Add form title getter"""
        translate = self.request.localizer.translate
        thesaurus = get_parent(self.context, IThesaurus)
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(
                get_object_label(thesaurus, self.request, self)),
            translate(_("New thesaurus extract")))


@ajax_form_config(name='add-extract.html',
                  context=IThesaurus, layer=IPyAMSLayer,
                  permission=ADMIN_THESAURUS_PERMISSION)
class ThesaurusExtractAddForm(ThesaurusExtractAddFormMixin, AdminModalAddForm):
    """Thesaurus extract add form"""

    legend = _("New extract properties")

    fields = Fields(IThesaurusExtract)
    content_factory = IThesaurusExtract

    def add(self, obj):
        extracts = IThesaurusExtracts(self.context)
        extracts[obj.name] = obj


#
# Thesaurus extract clone form
#

@adapter_config(name='clone',
                required=(IThesaurus, IAdminLayer, ThesaurusExtractsTable),
                provides=IColumn)
class ThesaurusExtractCloneColumn(ActionColumn):
    """Thesaurus extract clone column"""

    hint = _("Clone thesaurus extract")
    icon_class = 'far fa-clone'

    href = 'clone-extract.html'
    permission = ADMIN_THESAURUS_PERMISSION

    weight = 100


@ajax_form_config(name='clone-extract.html',
                  context=IThesaurusExtract, layer=IPyAMSLayer,
                  permission=ADMIN_THESAURUS_PERMISSION)
class ThesaurusExtractCloneForm(ThesaurusExtractAddFormMixin, AdminModalAddForm):
    """Thesaurus extract clone form"""

    legend = _("Clone thesaurus extract")

    fields = Fields(IThesaurusExtract).select('name')

    def create(self, data):
        return copy(self.context)

    def add(self, obj):
        source = IThesaurusExtract(self.context).name
        target = obj.name
        extracts = IThesaurusExtracts(self.context.__parent__)
        extracts[target] = obj
        thesaurus = get_parent(obj, IThesaurus)
        for term in thesaurus.terms:
            if source in term.extracts:
                term.add_extract(target)


#
# Thesaurus extract edit form
#

@adapter_config(required=(IThesaurusExtract, IAdminLayer, Interface),
                provides=ITableElementEditor)
class ThesaurusExtractElementEditor(TableElementEditor):
    """Thesaurus extract element editor"""

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        if not request.has_permission(MANAGE_THESAURUS_EXTRACT_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)


@ajax_form_config(name='properties.html',
                  context=IThesaurusExtract, layer=IPyAMSLayer,
                  permission=MANAGE_THESAURUS_EXTRACT_PERMISSION)
class ThesaurusExtractEditForm(AdminModalEditForm):
    """Thesaurus extract edit form"""

    @property
    def title(self):
        """Form title getter"""
        translate = self.request.localizer.translate
        thesaurus = get_parent(self.context, IThesaurus)
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(
                get_object_label(thesaurus, self.request, self)),
            translate(_("Thesaurus extract: {}")).format(self.context.name))

    legend = _("Extract properties")

    fields = Fields(IThesaurusExtract)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        name = self.widgets.get('name')
        if name is not None:
            name.mode = DISPLAY_MODE


@adapter_config(required=(IThesaurusExtract, IAdminLayer, ThesaurusExtractEditForm),
                provides=IAJAXFormRenderer)
class ThesaurusExtractEditFormAJAXRenderer(ContextRequestViewAdapter):
    """Thesaurus extract edit form AJAX renderer"""

    def render(self, changes):
        """AJAX result renderer"""
        if not changes:
            return None
        if 'color' in changes.get(IThesaurusExtractInfo, ()):
            return {
                'status': 'reload'
            }
        thesaurus = get_parent(self.context, IThesaurus)
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(thesaurus, self.request,
                                                    ThesaurusExtractsTable, self.context)
            ]
        }


@adapter_config(name='roles',
                required=(IThesaurusExtract, IAdminLayer, ThesaurusExtractEditForm),
                provides=IInnerSubForm)
class ThesaurusExtractRolesEditForm(Group):
    """Thesaurus extract roles edit form"""

    legend = _("Extract roles")

    fields = Fields(IThesaurusExtractRoles)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        managers = self.widgets.get('managers')
        if managers is not None:
            if not self.request.has_permission(ADMIN_THESAURUS_PERMISSION, context=self.context):
                managers.mode = DISPLAY_MODE


#
# Thesaurus extract tree view
#

@pagelet_config(name='terms-view.html',
                context=IThesaurusExtract, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusExtractTermsView(AdminModalDisplayForm):
    """Thesaurus extract terms view"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        thesaurus = get_parent(self.context, IThesaurus)
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(
                get_object_label(thesaurus, self.request, self)),
            translate(_("Thesaurus extract: {}")).format(self.context.name))

    legend = _("Extract terms")


@viewlet_config(name='extract-term',
                context=IThesaurusExtract, layer=IAdminLayer, view=ThesaurusExtractTermsView,
                manager=IContentSuffixViewletManager, weight=10,
                permission=VIEW_SYSTEM_PERMISSION)
@template_config(template='templates/extract-terms.pt', layer=IAdminLayer)
class ThesaurusExtractTermsTree(Viewlet):
    """Thesaurus extract terms tree view"""

    @property
    def tree(self):
        """Terms tree content getter"""
        thesaurus = get_parent(self.context, IThesaurus)
        extract = self.context.name
        return sorted((
            INode(node)
            for node in ITree(thesaurus).get_root_nodes()
            if extract in (node.extracts or ())
        ), key=lambda x: (x.order or 999, x.label))


@view_config(name='get-nodes.json',
             context=IThesaurusExtract, request_type=IPyAMSLayer,
             permission=VIEW_SYSTEM_PERMISSION,
             renderer='json', xhr=True)
def get_extract_nodes(request):
    """Get thesaurus extract nodes"""
    label = request.params.get('term')
    if label:
        label = unescape(label)
    thesaurus = get_parent(request.context, IThesaurus)
    term = thesaurus.terms.get(label)
    if term is None:
        raise HTTPNotFound
    result = []
    request.context.get_nodes(term, result)
    return {
        'term': label,
        'nodes': result
    }
