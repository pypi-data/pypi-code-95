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

"""PyAMS_thesaurus.zmi.tree module

This module defines components which are used to manage thesaurus terms tree.
"""

import json
from html import unescape

from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from zope.interface import Interface

from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.menu import MenuItem
from pyams_template.template import template_config
from pyams_thesaurus.interfaces import MANAGE_THESAURUS_CONTENT_PERMISSION, \
    MANAGE_THESAURUS_EXTRACT_PERMISSION
from pyams_thesaurus.interfaces.extension import IThesaurusTermExtension
from pyams_thesaurus.interfaces.loader import IThesaurusExporter, IThesaurusExporterConfiguration, \
    IThesaurusLoader, IThesaurusUpdaterConfiguration
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtracts
from pyams_thesaurus.loader.config import ThesaurusExporterConfiguration, \
    ThesaurusUpdaterConfiguration
from pyams_thesaurus.zmi.interfaces import IThesaurusTermsTreeMenu
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tree import INode, ITree
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import ViewContentProvider, viewlet_config
from pyams_zmi.form import AdminModalAddForm
from pyams_zmi.interfaces import IAdminLayer, ICompositeView
from pyams_zmi.interfaces.viewlet import IActionsViewletManager, IContentManagementMenu
from pyams_zmi.view import CompositeAdminView
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


@viewletmanager_config(name='terms-tree.menu',
                       context=IThesaurus, layer=IAdminLayer,
                       manager=IContentManagementMenu, weight=20,
                       provides=IThesaurusTermsTreeMenu,
                       permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusTermsTreeMenu(NavigationMenuItem):
    """Thesaurus terms tree menu"""

    label = _("Terms tree")
    icon_class = 'fas fa-tags'

    href = '#terms-view.html'


@pagelet_config(name='terms-view.html',
                context=IThesaurus, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusTermsView(CompositeAdminView):
    """Thesaurus terms and extracts view"""


#
# Thesaurus terms tree view
#

@adapter_config(name='terms-tree.view',
                required=(IThesaurus, IAdminLayer, ThesaurusTermsView),
                provides=ICompositeView)
@template_config(template='templates/terms-tree.pt', layer=IAdminLayer)
class ThesaurusTermsTreeView(ViewContentProvider):
    """Thesaurus terms tree view"""

    title = _("Terms tree view")

    weight = 20

    @property
    def extracts(self):
        """Thesaurus extracts getter"""
        return IThesaurusExtracts(self.context)

    @property
    def tree(self):
        """Terms tree root nodes getter"""
        return [
            INode(node)
            for node in ITree(self.context).get_root_nodes()
        ]

    @property
    def search_query_params(self):
        """Terms search query params getter"""
        return json.dumps({
            'thesaurus_name': self.context.name
        })


@view_config(name='get-nodes.json',
             context=IThesaurus, request_type=IPyAMSLayer,
             permission=VIEW_SYSTEM_PERMISSION,
             renderer='json', xhr=True)
def get_thesaurus_nodes(request):
    """Get thesaurus nodes"""
    label = request.params.get('term')
    if label:
        label = unescape(label)
    term = request.context.terms.get(label)
    if term is None:
        raise HTTPNotFound
    result = []
    request.context.get_nodes(term, result)
    return {
        'term': label,
        'nodes': result
    }


@view_config(name='get-parent-nodes.json',
             context=IThesaurus, request_type=IPyAMSLayer,
             permission=VIEW_SYSTEM_PERMISSION,
             renderer='json', xhr=True)
def get_parent_nodes(request):
    """Get thesaurus parent nodes of a given node"""
    label = request.params.get('term')
    if label:
        label = unescape(label)
    term = request.context.terms.get(label)
    if term is None:
        raise HTTPNotFound
    result = []
    parents = list(reversed(term.get_parents()))
    if parents:
        request.context.get_nodes(parents[0], result, [t.label for t in parents])
        return {
            'term': label,
            'nodes': result,
            'parent': parents[0].label
        }
    return {
        'term': label,
        'nodes': result,
        'parent': label
    }


@view_config(name='switch-extension.json',
             context=IThesaurus, request_type=IPyAMSLayer,
             permission=MANAGE_THESAURUS_CONTENT_PERMISSION,
             renderer='json', xhr=True)
def switch_term_extension(request):
    """Term extension switcher"""
    label = request.params.get('term')
    extension_name = request.params.get('extension')
    if not (label and extension_name):
        raise HTTPBadRequest("Missing argument(s)")
    thesaurus = request.context
    term = thesaurus.terms.get(unescape(label))
    if term is None:
        raise HTTPBadRequest("Term not found")
    extension = query_utility(IThesaurusTermExtension, name=extension_name)
    if extension is None:
        raise HTTPBadRequest("Extension not found")
    term.extensions = term.extensions | {extension_name}
    translate = request.localizer.translate
    return {
        'name': extension_name,
        'title': translate(extension.label),
        'icon': extension.icon_css_class,
        'view': absolute_url(term, request, extension.target_view),
        'active': extension_name in term.extensions
    }


@view_config(name='switch-extract.json',
             context=IThesaurus, request_type=IPyAMSLayer,
             permission=VIEW_SYSTEM_PERMISSION,
             renderer='json', xhr=True)
def switch_term_extract(request):
    """Term extract switcher"""
    label = request.params.get('term')
    extract_name = request.params.get('extract')
    if not (label and extract_name):
        raise HTTPBadRequest("Missing argument(s)")
    thesaurus = request.context
    term = thesaurus.terms.get(unescape(label))
    if term is None:
        raise HTTPBadRequest("Term not found")
    extract = IThesaurusExtracts(thesaurus).get(extract_name)
    if extract is None:
        raise HTTPBadRequest("Extract not found")
    if not request.has_permission(MANAGE_THESAURUS_EXTRACT_PERMISSION, context=extract):
        raise HTTPForbidden("You are not authorized to update this extract")
    if extract.name in (term.extracts or ()):
        extract.remove_term(term)
    else:
        extract.add_term(term)
    return {
        'term': term.label,
        'extract': extract.name,
        'color': extract.color,
        'used': extract.name in term.extracts
    }


#
# Import menu
#

@viewlet_config(name='import-terms.action',
                context=IThesaurus, layer=IAdminLayer, view=ThesaurusTermsTreeView,
                manager=IActionsViewletManager, weight=10,
                permission=MANAGE_THESAURUS_CONTENT_PERMISSION)
class ThesaurusImportAction(MenuItem):
    """Thesaurus import action"""

    label = _("Import terms")
    icon_class = 'fas fa-upload'

    href = 'import-terms.html'
    modal_target = True


class IThesaurusImportFormButtons(Interface):
    """Thesaurus import form buttons interface"""

    add = SubmitButton(name='add',
                       title=_("Import terms"))

    close = CloseButton(name='close',
                        title=_("Cancel"))


@ajax_form_config(name='import-terms.html',
                  context=IThesaurus, layer=IPyAMSLayer,
                  permission=MANAGE_THESAURUS_CONTENT_PERMISSION)
class ThesaurusImportForm(AdminModalAddForm):
    """Thesaurus import form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(self.context.name),
            translate(_("Import new terms")))

    legend = _("Import thesaurus terms")

    fields = Fields(IThesaurusUpdaterConfiguration).select('clear', 'conflict_suffix', 'data',
                                                           'format', 'import_synonyms',
                                                           'language', 'encoding')
    buttons = Buttons(IThesaurusImportFormButtons)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        language = self.widgets.get('language')
        if language is not None:
            language.no_value_message = _("-- automatic detection -- (if available)")
        encoding = self.widgets.get('encoding')
        if encoding is not None:
            encoding.no_value_message = _("-- automatic detection -- (if available)")

    @handler(IThesaurusImportFormButtons['add'])
    def handle_import(self, action):
        """Import action handler"""
        super().handle_add(self, action)  # pylint: disable=too-many-function-args

    def create(self, data):
        return ThesaurusUpdaterConfiguration()

    def add(self, config):  # pylint: disable=arguments-renamed
        loader = get_utility(IThesaurusLoader, name=config.format)
        source = loader.load(config.data, config)
        target = self.context
        if config.clear:
            target.clear()
        target.merge(config, source)


@adapter_config(required=(IThesaurus, IAdminLayer, ThesaurusImportForm),
                provides=IAJAXFormRenderer)
class ThesaurusImportFormRenderer(ContextRequestViewAdapter):
    """Thesaurus import form renderer"""

    def render(self, changes):  # pylint: disable=no-self-use
        """AJAX form renderer"""
        if changes is None:
            return None
        return {
            'status': 'reload'
        }


#
# Thesaurus export form
#

@viewlet_config(name='export-terms.action',
                context=IThesaurus, layer=IAdminLayer, view=ThesaurusTermsTreeView,
                manager=IActionsViewletManager, weight=20,
                permission=MANAGE_THESAURUS_CONTENT_PERMISSION)
class ThesaurusExportAction(MenuItem):
    """Thesaurus export action"""

    label = _("Export terms")
    icon_class = 'fas fa-download'

    href = 'export-terms.html'
    modal_target = True


class IThesaurusExportFormButtons(Interface):
    """Thesaurus export form buttons interface"""

    export = SubmitButton(name='export',
                          title=_("terms-export-button", default="Export terms"))

    close = CloseButton(name='close',
                        title=_("Cancel"))


@ajax_form_config(name='export-terms.html',  # pylint: disable=abstract-method
                  context=IThesaurus, layer=IPyAMSLayer,
                  permission=MANAGE_THESAURUS_CONTENT_PERMISSION,
                  ajax_xhr=False, ajax_require_csrf=False)
class ThesaurusExportForm(AdminModalAddForm):
    """Thesaurus export form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(self.context.name),
            translate(_("terms-export-title", default="Export terms")))

    legend = _("Export thesaurus terms")

    fields = Fields(IThesaurusExporterConfiguration)
    buttons = Buttons(IThesaurusExportFormButtons)

    object_data = {
        'ams-form-download-target': 'thesaurus-export-frame'
    }

    exporter = None

    @handler(IThesaurusExportFormButtons['export'])
    def handle_export(self, action):
        """Export action handler"""
        super().handle_add(self, action)  # pylint: disable=too-many-function-args

    def create_and_add(self, data):
        data = data.get(self, {})
        config = ThesaurusExporterConfiguration(data)
        self.exporter = get_utility(IThesaurusExporter, name=config.format)
        target = self.exporter.export(self.context, config)
        return target, config


@adapter_config(required=(IThesaurus, IAdminLayer, ThesaurusExportForm),
                provides=IAJAXFormRenderer)
class ThesaurusExportFormRenderer(ContextRequestViewAdapter):
    """Thesaurus export form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        target, config = changes
        target.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="{0}"'.format(config.filename),
            'Content-Type': self.view.exporter.handler.content_type
        }
        response = Response(headers=headers)
        response.body_file = target
        return response
