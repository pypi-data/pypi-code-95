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

"""PyAMS_thesaurus.zmi.term module

This module provides all terms related management components.
"""

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_skin.viewlet.actions import ContextAction
from pyams_thesaurus.interfaces import MANAGE_THESAURUS_CONTENT_PERMISSION
from pyams_thesaurus.interfaces.term import IThesaurusTerm
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_thesaurus.zmi.tree import ThesaurusTermsTreeView
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import get_object_factory
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


@viewlet_config(name='add-term.menu',
                context=IThesaurus, layer=IAdminLayer, view=ThesaurusTermsTreeView,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_THESAURUS_CONTENT_PERMISSION)
class ThesaurusTermAddMenu(ContextAction):
    """Term add menu"""

    status = 'success'
    icon_class = 'fas fa-plus'
    label = _("Add term")

    href = 'add-term.html'
    modal_target = True


@ajax_form_config(name='add-term.html',
                  context=IThesaurus, layer=IPyAMSLayer,
                  permission=MANAGE_THESAURUS_CONTENT_PERMISSION)
class ThesaurusTermAddForm(AdminModalAddForm):
    """Term add form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(self.context.name),
            translate(_("Create new term")))

    legend = _("New term properties")

    fields = Fields(IThesaurusTerm).select('label', 'alt', 'definition', 'note', 'generic',
                                           'order', 'associations', 'usage', 'extensions',
                                           'status', 'created')
    content_factory = IThesaurusTerm

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        for name in ('generic', 'associations', 'usage'):
            if name in self.widgets:
                self.widgets[name].thesaurus_name = self.context.name

    def create(self, data):
        factory = get_object_factory(self.content_factory)
        if factory is not None:
            return factory(data.get('label'))
        raise NotImplementedError

    def update_content(self, obj, data):
        changes = super().update_content(obj, data)
        generic = obj.generic
        usage = obj.usage
        if (generic is None) and (usage is None):
            IThesaurus(self.context).top_terms += [obj]
        else:
            if generic is not None:
                generic.specifics += [obj]
            elif usage is not None:
                usage.used_for += [obj]
        return changes

    def add(self, obj):
        self.context.terms[obj.label] = obj


@adapter_config(required=(IThesaurus, IAdminLayer, ThesaurusTermAddForm),
                provides=IAJAXFormRenderer)
class ThesaurusTermAddFormRenderer(ContextRequestViewAdapter):
    """Thesaurus term add form AJAX renderer"""

    def render(self, changes):  # pylint: disable=no-self-use
        """JSON form renderer"""
        if changes is None:
            return None
        label = changes.label.replace("'", "&#039;")
        return {
            'status': 'success',
            'callbacks': [{
                'callback': 'MyAMS.thesaurus.tree.findTerm',
                'options': {
                    'term': label
                }
            }]
        }


@ajax_form_config(name='properties.html',
                  context=IThesaurusTerm, layer=IPyAMSLayer,
                  permission=VIEW_SYSTEM_PERMISSION)
class ThesaurusTermEditForm(AdminModalEditForm):
    """Thesaurus term edit form"""

    @property
    def title(self):
        """Form title getter"""
        translate = self.request.localizer.translate
        thesaurus = get_parent(self.context, IThesaurus)
        return '<small>{}</small><br />{}'.format(
            translate(_("Thesaurus: {}")).format(thesaurus.name),
            translate(_("Term: {}")).format(self.context.label))

    legend = _("Thesaurus term properties")

    fields = Fields(IThesaurusTerm).select('label', 'alt', 'definition', 'note', 'generic',
                                           'order', 'specifics', 'associations', 'usage',
                                           'used_for', 'extracts', 'extensions', 'status',
                                           'created', 'modified')

    generic_changed = False
    usage_changed = False

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        thesaurus = get_parent(self.context, IThesaurus)
        for name in ('generic', 'specifics', 'associations', 'usage', 'used_for'):
            if name in self.widgets:
                self.widgets[name].thesaurus_name = thesaurus.name
        for name in ('specifics', 'used_for', 'extracts', 'created'):
            if name in self.widgets:
                self.widgets[name].mode = DISPLAY_MODE

    def apply_changes(self, data):  # pylint: disable=too-many-branches
        term = self.context
        thesaurus = get_parent(term, IThesaurus)
        old_label = term.label
        old_generic = term.generic
        old_usage = term.usage
        changes = super().apply_changes(data)
        # Move term if label changed
        if 'label' in changes.get(IThesaurusTerm, ()):
            terms = thesaurus.terms
            del terms[old_label]  # pylint: disable=unsupported-delete-operation
            terms[term.label] = term  # pylint: disable=unsupported-assignment-operation
        # Check modifications
        self.generic_changed = old_generic != term.generic
        self.usage_changed = old_usage != term.usage
        # Check generic change
        if self.generic_changed:
            if old_generic is not None:
                # Add a previous generic?
                # => remove term from list of previous term's specifics
                specifics = old_generic.specifics
                if term in specifics:
                    specifics.remove(term)
                    old_generic.specifics = specifics
            else:
                # No previous generic?
                # => remove term from thesaurus top terms
                top_terms = thesaurus.top_terms
                if term in top_terms:
                    top_terms.remove(term)
                    thesaurus.top_terms = top_terms
            # Check new value
            if term.generic is None:
                # No generic and not a synonym?
                # => add term to top terms
                if (term.usage is None) and (term not in thesaurus.top_terms):
                    thesaurus.top_terms += [term, ]
            else:
                # New generic?
                # => add term to generic specific terms
                if term not in term.generic.specifics:
                    term.generic.specifics += [term, ]
        # Check usage change
        if self.usage_changed:
            if old_usage is not None:
                # Add previous usage term?
                # => update used_for
                used_for = old_usage.used_for
                if term in used_for:
                    used_for.remove(term)
                    old_usage.used_for = used_for
            # Check new term usage
            if term.usage is None:
                # No usage
                # => maybe a top term...
                if (term.generic is None) and (term not in thesaurus.top_terms):
                    thesaurus.top_terms += [term, ]
            else:
                # Term usage?
                # => remove term from top terms
                top_terms = thesaurus.top_terms
                if term in top_terms:
                    top_terms.remove(term)
                    thesaurus.top_terms = top_terms
                # Add term to usage synonyms
                if term not in term.usage.used_for:
                    term.usage.used_for += [term, ]
        return changes


@adapter_config(required=(IThesaurusTerm, IAdminLayer, ThesaurusTermEditForm),
                provides=IAJAXFormRenderer)
class ThesaurusTermEditFormRenderer(ContextRequestViewAdapter):
    """Thesaurus term edit form renderer"""

    def render(self, changes):
        """AJAX edit form renderer"""
        if changes is None:
            return None
        term = self.context
        term_changes = changes.get(IThesaurusTerm, ())
        if self.view.generic_changed or ('order' in term_changes):
            label = term.label.replace("'", "&#039;")
            return {
                'status': 'reload',
                'postReload': 'MyAMS.thesaurus.tree.findMovedTerm',
                'postReloadOptions': {
                    'term': label
                }
            }
        if ('status' in term_changes) or \
                ('label' in term_changes) or \
                ('extensions' in term_changes):
            label = (term.generic or term).label.replace("'", "&#039;")
            return {
                'status': 'callback',
                'callback': 'MyAMS.thesaurus.tree.updateTerm',
                'options': {
                    'term': label
                }
            }
        return None
