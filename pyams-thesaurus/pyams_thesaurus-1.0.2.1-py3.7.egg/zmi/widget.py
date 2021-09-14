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

"""PyAMS_thesaurus.zmi.widget module

This module defines custom widgets which are used to handle thesaurus terms
selection.
"""

import json
import re

from pyramid.decorator import reify
from zope.component import queryMultiAdapter
from zope.interface import directlyProvides, implementer_only
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm

from pyams_form.browser.select import SelectWidget
from pyams_form.converter import SequenceDataConverter
from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_thesaurus.interfaces.term import IThesaurusTerm, STATUS_ARCHIVED
from pyams_thesaurus.interfaces.thesaurus import IThesaurus
from pyams_thesaurus.schema import IThesaurusTermField, IThesaurusTermsListField
from pyams_thesaurus.zmi.interfaces import IThesaurusTermWidget, IThesaurusTermsListWidget, \
    IThesaurusTermsTreeWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.registry import query_utility
from pyams_utils.traversing import get_parent


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


class SimpleThesaurusTerm(SimpleTerm):
    """Simple thesaurus term"""

    def __init__(self, value, token=None, title=None):  # pylint: disable=super-init-not-called
        self.value = value
        self.token = token or value
        self.title = title
        if title is not None:
            directlyProvides(self, ITitledTokenizedTerm)


class ThesaurusWidgetMixin:
    """Thesaurus base widget mixin"""

    @reify
    def thesaurus(self):
        """Thesaurus utility getter"""
        content = self.form.get_content()
        if IThesaurusTerm.providedBy(content):
            content = get_parent(content, IThesaurus)
        if IThesaurus.providedBy(content):
            thesaurus = content
        else:
            thesaurus = queryMultiAdapter((content, self.request, self.form),
                                          IThesaurus, name=self.field.__name__)
            if thesaurus is None:
                name = self.thesaurus_name
                thesaurus = query_utility(IThesaurus, name=name)
        return thesaurus

    def is_selected(self, term):
        """Check for term selection"""
        return term.token in self.value


def thesaurus_widget_term_factory(term, widget):
    """Thesaurus term factory"""
    if not IThesaurusTerm.providedBy(term):
        thesaurus = widget.thesaurus
        if thesaurus is not None:
            term = thesaurus.terms.get(term)
    if IThesaurusTerm.providedBy(term):
        return SimpleThesaurusTerm(term.label, title=term.label)
    return None


#
# Term widget
#

SYNONYM = re.compile(r'(.*) \[ .* \]')


@adapter_config(required=(IThesaurusTermField, IThesaurusTermWidget),
                provides=IDataConverter)
class ThesaurusTermDataConverter(SequenceDataConverter):
    """Thesaurus term data converter"""

    def to_widget_value(self, value):
        # Widget expects term label or caption
        if isinstance(value, (set, list, tuple)):
            try:
                value = next(iter(value))
            except StopIteration:
                value = None
        if IThesaurusTerm.providedBy(value):
            value = value.label
        return super().to_widget_value(value)

    def to_field_value(self, value):
        # Field expects thesaurus term instance
        if not value:
            return self.field.missing_value
        thesaurus = self.widget.thesaurus
        if thesaurus is None:
            return None
        if isinstance(value, (set, list, tuple)):
            try:
                value = next(iter(value))
            except StopIteration:
                value = None
        if value == self.widget.no_value_token:
            return None
        match = SYNONYM.match(value)
        if match:
            value = match.groups()[0]
        return thesaurus.terms.get(value)


@implementer_only(IThesaurusTermWidget)
class ThesaurusTermWidget(ThesaurusWidgetMixin, SelectWidget):
    """Thesaurus term widget"""

    ajax_url = '/api/thesaurus/terms'
    placeholder = _("No selected term")

    thesaurus_name = FieldProperty(IThesaurusTermWidget['thesaurus_name'])
    extract_name = FieldProperty(IThesaurusTermWidget['extract_name'])

    @property
    def ajax_params(self):
        """AJAX request params getter"""
        return json.dumps({
            'thesaurus_name': self.thesaurus_name,
            'extract_name': self.extract_name
        })

    def term_factory(self, value):
        """Selected term factory"""
        return thesaurus_widget_term_factory(value, self)


@adapter_config(required=(IThesaurusTermField, IFormLayer),
                provides=IFieldWidget)
def ThesaurusTermFieldWidget(field, request):  # pylint: disable=invalid-name
    """Thesaurus term field widget factory"""
    return FieldWidget(field, ThesaurusTermWidget(request))


#
# Terms list widget
#

@adapter_config(required=(IThesaurusTermsListField, IThesaurusTermsListWidget),
                provides=IDataConverter)
class ThesaurusTermsListDataConverter(SequenceDataConverter):
    """Thesaurus terms list data converter"""

    def to_widget_value(self, value):
        # Widget expects a list of thesaurus terms labels or captions
        if value is self.field.missing_value:
            return []
        return [term.label for term in value]

    def to_field_value(self, value):
        # Field expects a list of thesaurus terms
        if not value:
            return self.field.missing_value
        thesaurus = self.widget.thesaurus
        if thesaurus is None:
            return None
        if isinstance(value, str):
            value = value.split('|')
        for idx, val in enumerate(value):
            if val == self.widget.no_value_token:
                continue
            match = SYNONYM.match(val)
            if match:
                value[idx] = match.groups()[0]
        terms = thesaurus.terms
        return [
            terms.get(term)
            for term in value
            if term != self.widget.no_value_token
        ]


@implementer_only(IThesaurusTermsListWidget)
class ThesaurusTermsListWidget(ThesaurusWidgetMixin, SelectWidget):
    """Thesaurus terms list widget"""

    ajax_url = '/api/thesaurus/terms'
    placeholder = _("No selected term")

    multiple = 'multiple'

    thesaurus_name = FieldProperty(IThesaurusTermsListWidget['thesaurus_name'])
    extract_name = FieldProperty(IThesaurusTermsListWidget['extract_name'])

    @property
    def ajax_params(self):
        """AJAX request params getter"""
        return json.dumps({
            'thesaurus_name': self.thesaurus_name,
            'extract_name': self.extract_name
        })

    def term_factory(self, value):
        """Selected term factory"""
        return thesaurus_widget_term_factory(value, self)


@adapter_config(required=(IThesaurusTermsListField, IFormLayer),
                provides=IFieldWidget)
def ThesaurusTermsListFieldWidget(field, request):  # pylint: disable=invalid-name
    """Thesaurus terms list field widget factory"""
    return FieldWidget(field, ThesaurusTermsListWidget(request))


@implementer_only(IThesaurusTermsTreeWidget)
class ThesaurusTermsTreeWidget(ThesaurusTermsListWidget):
    """Thesaurus terms tree widget"""

    @property
    def top_terms(self):
        """Thesaurus top terms getter"""
        thesaurus = self.thesaurus
        if thesaurus is None:
            return ()
        return sorted(thesaurus.get_top_terms(extract=self.extract_name),
                      key=lambda x: (x.order or 999, x.label))

    def get_subterms(self, term):
        """Get sub-terms from given term"""
        for subterm in term.specifics:
            if (not self.extract_name) or (self.extract_name in subterm.extracts):
                if subterm.status != STATUS_ARCHIVED:
                    yield subterm
                    yield from self.get_subterms(subterm)


def ThesaurusTermsTreeFieldWidget(field, request):  # pylint: disable=invalid-name
    """Thesaurus terms tree field widget factory"""
    return FieldWidget(field, ThesaurusTermsTreeWidget(request))
