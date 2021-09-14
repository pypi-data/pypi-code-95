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

"""PyAMS_thesaurus.term module

This module defines main thesaurus terms class.
"""

from datetime import datetime

from persistent import Persistent
from pyramid.events import subscriber
from zope.container.contained import Contained
from zope.interface import alsoProvides, noLongerProvides
from zope.interface.interfaces import ComponentLookupError
from zope.lifecycleevent import IObjectAddedEvent, IObjectModifiedEvent, IObjectMovedEvent, \
    IObjectRemovedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable

from pyams_catalog.utils import index_object, reindex_object, unindex_object
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_thesaurus.interfaces import MANAGE_THESAURUS_CONTENT_PERMISSION
from pyams_thesaurus.interfaces.extension import IThesaurusTermExtension, \
    THESAURUS_EXTENSIONS_VOCABULARY
from pyams_thesaurus.interfaces.term import IThesaurusLoaderTerm, IThesaurusTerm, \
    IThesaurusTermsContainer, STATUS_PUBLISHED
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusExtract
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.interfaces.tree import INode
from pyams_utils.registry import get_pyramid_registry, query_utility
from pyams_utils.request import check_request
from pyams_utils.timezone import tztime
from pyams_utils.traversing import get_parent
from pyams_utils.unicode import translate_string
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'


REVERSE_LINK_ATTRIBUTES = {
    'generic': 'specifics',
    'usage': 'used_for'
}

REVERSE_LIST_ATTRIBUTES = {
    'specifics': 'generic',
    'used_for': 'usage'
}


@adapter_config(name='terms',
                required=IThesaurus,
                provides=ITraversable)
class ThesaurusTermsNamespace(ContextAdapter):
    """Thesaurus ++terms++ namespace"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Namespace traverser"""
        terms = IThesaurus(self.context).terms
        if name:
            return terms[name]
        return terms


@factory_config(IThesaurusTerm)  # pylint: disable=too-many-instance-attributes
class ThesaurusTerm(Persistent, Contained):
    """Thesaurus term"""

    label = FieldProperty(IThesaurusTerm['label'])
    alt = FieldProperty(IThesaurusTerm['alt'])
    definition = FieldProperty(IThesaurusTerm['definition'])
    note = FieldProperty(IThesaurusTerm['note'])
    _generic = FieldProperty(IThesaurusTerm['generic'])
    order = FieldProperty(IThesaurusTerm['order'])
    _specifics = FieldProperty(IThesaurusTerm['specifics'])
    _associations = FieldProperty(IThesaurusTerm['associations'])
    _usage = FieldProperty(IThesaurusTerm['usage'])
    _used_for = FieldProperty(IThesaurusTerm['used_for'])
    _extracts = FieldProperty(IThesaurusTerm['extracts'])
    _extensions = FieldProperty(IThesaurusTerm['extensions'])
    status = FieldProperty(IThesaurusTerm['status'])
    micro_thesaurus = FieldProperty(IThesaurusTerm['micro_thesaurus'])
    parent = FieldProperty(IThesaurusTerm['parent'])
    _created = FieldProperty(IThesaurusTerm['created'])
    _modified = FieldProperty(IThesaurusTerm['modified'])

    def __init__(self, label, alt=None, definition=None, note=None,  # pylint: disable=too-many-arguments,too-many-instance-attributes
                 generic=None, specifics=None, associations=None,
                 usage=None, used_for=None, created=None, modified=None):
        self.label = label
        self.alt = alt
        self.definition = definition
        self.note = note
        self.generic = generic
        self.specifics = specifics or []
        self.associations = associations or []
        self.usage = usage
        self.used_for = used_for or []
        self.created = created
        self.modified = modified

    def __eq__(self, other):
        if other is None:
            return False
        return isinstance(other, ThesaurusTerm) and (self.label == other.label)

    def __hash__(self):
        return hash(self.label)

    @property
    def base_label(self):
        """Get translated label"""
        return translate_string(self.label, escape_slashes=True, force_lower=True, spaces=' ')

    @property
    def title(self):
        """Complete title getter"""
        if self._usage:
            label = self._usage.label
            terms = [
                term.label for term in self._usage.used_for
                if term.status == STATUS_PUBLISHED
            ]
        elif self._used_for:
            label = self.label
            terms = [
                term.label for term in self._used_for
                if term.status == STATUS_PUBLISHED
            ]
        else:
            label = self.label
            terms = []
        return label + (' [ {0} ]'.format(', '.join(terms)) if terms else '')

    @property
    def generic(self):
        """Generic term getter"""
        return self._generic

    @generic.setter
    def generic(self, value):
        """Generic term setter"""
        self._generic = value
        if value is not None:
            self.extracts = self.extracts & value.extracts

    @property
    def specifics(self):
        """Specific terms getter"""
        return sorted(self._specifics,
                      key=lambda x: (x.order or 999, x.label))

    @specifics.setter
    def specifics(self, value):
        """Specific terms setter"""
        self._specifics = list(value or ())

    @property
    def associations(self):
        """Associated terms getter"""
        return self._associations

    @associations.setter
    def associations(self, value):
        """Associated terms setter"""
        self._associations = list(value or ())

    @property
    def usage(self):
        """Usage term getter"""
        return self._usage

    @usage.setter
    def usage(self, value):
        """Usage term setter"""
        self._usage = value
        if value is not None:
            self.generic = None
            self.extracts = value.extracts

    @property
    def used_for(self):
        """Used for term getter"""
        return self._used_for

    @used_for.setter
    def used_for(self, value):
        """Used for term setter"""
        self._used_for = list(value or ())

    @property
    def extracts(self):
        """Term extracts getter"""
        return self._extracts or set()

    @extracts.setter
    def extracts(self, value):
        """Term extracts setter"""
        old_value = self._extracts or set()
        new_value = value or set()
        if self._generic is not None:
            new_value = new_value & (self._generic.extracts or set())
        if old_value != new_value:
            removed = old_value - new_value
            if removed:
                for term in self.specifics:
                    term.extracts = (term.extracts or set()) - removed
            self._extracts = new_value
            # Extracts selection also applies to term synonyms...
            for term in self.used_for or ():
                term.extracts = self.extracts

    def add_extract(self, extract, check=True):
        """Add term to given extract"""
        if IThesaurusExtract.providedBy(extract):  # pylint: disable=no-value-for-parameter
            extract = extract.name
        if check:
            self.extracts = (self.extracts or set()) | {extract}
        else:
            self._extracts = (self._extracts or set()) | {extract}
            # Extracts selection also applies to term synonyms...
            for term in self.used_for or ():
                term.extracts = self.extracts

    def remove_extract(self, extract, check=True):
        """Removed term from given extract"""
        if IThesaurusExtract.providedBy(extract):  # pylint: disable=no-value-for-parameter
            extract = extract.name
        if check:
            self.extracts = (self.extracts or set()) - {extract}
        else:
            self._extracts = (self._extracts or set()) - {extract}
            # Extracts selection also applies to term synonyms...
            for term in self.used_for or ():
                term.extracts = self.extracts

    @property
    def extensions(self):
        """Term extensions getter"""
        return self._extensions or set()

    @extensions.setter
    def extensions(self, value):
        """Term extensions setter"""
        old_value = self._extensions or set()
        new_value = value or set()
        if old_value != new_value:
            added = new_value - old_value
            removed = old_value - new_value
            for ext in removed:
                extension = query_utility(IThesaurusTermExtension, ext)
                if extension is not None:
                    noLongerProvides(self, extension.target_interface)
            for ext in added:
                extension = query_utility(IThesaurusTermExtension, ext)
                if extension is not None:
                    alsoProvides(self, extension.target_interface)
            self._extensions = new_value

    def query_extensions(self):
        """Query term extensions"""
        return sorted([
            util for util in [
                query_utility(IThesaurusTermExtension, ext)
                for ext in self.extensions
            ]
            if util is not None
        ], key=lambda x: getattr(x, 'weight', 999))

    @property
    def created(self):
        """Creation date getter"""
        return self._created

    @created.setter
    def created(self, value):
        """Creation date setter"""
        if isinstance(value, str):
            if ' ' in value:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                value = datetime.strptime(value, '%Y-%m-%d')
        self._created = tztime(value)

    @property
    def modified(self):
        """Modified date getter"""
        return self._modified

    @modified.setter
    def modified(self, value):
        """Modified date setter"""
        if isinstance(value, str):
            if ' ' in value:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            else:
                value = datetime.strptime(value, '%Y-%m-%d')
        self._modified = tztime(value)

    def get_parents(self):
        """Term parents getter"""
        terms = []
        parent = self.generic
        while parent is not None:
            terms.append(parent)
            parent = parent.generic
        return terms

    @property
    def level(self):
        """Term depth level getter"""
        return len(self.get_parents()) + 1

    def get_siblings(self):
        """Term siblings getter"""
        terms = []
        parent = self.generic
        if parent is not None:
            for term in parent.specifics:
                if term is not self:
                    terms.append(term)
        return terms

    def get_all_children(self, terms=None, with_synonyms=False):
        """Term children getter"""
        if terms is None:
            terms = []
        if with_synonyms:
            terms.extend(self.used_for)
        terms.extend(self.specifics)
        for term in self.specifics:
            term.get_all_children(terms, with_synonyms)
        return terms

    def short_url(self):
        """Short URL getter"""
        thesaurus = get_parent(self, IThesaurus)
        return '{}/{}'.format(thesaurus.__name__, self.__name__)

    def merge(self, term, configuration):  # pylint: disable=too-many-branches,too-many-statements
        """Merge existing term with provided one"""
        # terms marked by IThesaurusLoaderTerm interface are used by custom loaders which
        # only contains synonyms definitions; so they shouldn't alter terms properties
        if term is None:
            return
        # assign basic attributes
        if not IThesaurusLoaderTerm.providedBy(term):  # pylint: disable=no-value-for-parameter
            for name in ('label', 'definition', 'note', 'status', 'micro_thesaurus',
                         'created', 'modified'):
                setattr(self, name, getattr(term, name, None))
        # for term references, we have to check if the target term is already
        # in our parent thesaurus or not :
        #  - if yes => we target the term actually in the thesaurus
        #  - if not => we keep the same target, which will be included in the thesaurus
        #  after merging
        terms = self.__parent__
        if IThesaurusLoaderTerm.providedBy(term):  # pylint: disable=no-value-for-parameter
            attrs = ('usage',)
        else:
            attrs = ('generic', 'usage')
        for name in attrs:
            target = getattr(term, name)
            if target is None:
                setattr(self, name, None)
            else:
                label = target.label
                suffix = getattr(configuration, 'conflict_suffix', None)
                if suffix:
                    label = target.label + ' ' + suffix
                    if label not in terms:  # pylint: disable=unsupported-membership-test
                        label = target.label
                if label in terms:  # pylint: disable=unsupported-membership-test
                    target_term = terms[label]  # pylint: disable=unsubscriptable-object
                else:
                    target_term = target
                setattr(self, name, target_term)
                if name in REVERSE_LINK_ATTRIBUTES:
                    attribute = REVERSE_LINK_ATTRIBUTES[name]
                    setattr(target_term, attribute, set(getattr(target_term, attribute)) | {self})
        if IThesaurusLoaderTerm.providedBy(term):  # pylint: disable=no-value-for-parameter
            attrs = ('used_for',)
        else:
            attrs = ('specifics', 'associations', 'used_for')
        for name in attrs:
            targets = getattr(term, name, [])
            if not targets:
                setattr(self, name, [])
            else:
                new_targets = []
                for target in targets:
                    label = target.label
                    suffix = getattr(configuration, 'conflict_suffix', None)
                    if suffix:
                        label = target.label + ' ' + suffix
                        if label not in terms:  # pylint: disable=unsupported-membership-test
                            label = target.label
                    if label in terms:  # pylint: disable=unsupported-membership-test
                        target_term = terms[label]  # pylint: disable=unsubscriptable-object
                    else:
                        target_term = target
                    new_targets.append(target_term)
                    if name in REVERSE_LIST_ATTRIBUTES:
                        attribute = REVERSE_LIST_ATTRIBUTES[name]
                        setattr(target_term, attribute, self)
                setattr(self, name, new_targets)


@subscriber(IObjectAddedEvent, context_selector=IThesaurusTerm)
@subscriber(IObjectMovedEvent, context_selector=IThesaurusTerm)
def handle_new_term(event):
    """Index term into inner catalog"""
    if IThesaurusLoaderTerm.providedBy(event.object):  # pylint: disable=no-value-for-parameter
        return
    if IThesaurusTermsContainer.providedBy(event.oldParent):  # pylint: disable=no-value-for-parameter
        thesaurus = event.oldParent.__parent__
        if IThesaurus.providedBy(thesaurus):  # pylint: disable=no-value-for-parameter
            unindex_object(event.object, thesaurus.catalog)
    if IThesaurusTermsContainer.providedBy(event.newParent):  # pylint: disable=no-value-for-parameter
        thesaurus = event.newParent.__parent__
        if IThesaurus.providedBy(thesaurus):  # pylint: disable=no-value-for-parameter
            index_object(event.object, thesaurus.catalog)


@subscriber(IObjectModifiedEvent, context_selector=IThesaurusTerm)
def handle_modified_term(event):
    """Update index term into inner catalog"""
    parent = get_parent(event.object, IThesaurusTermsContainer)
    if parent is not None:
        thesaurus = parent.__parent__
        if IThesaurus.providedBy(thesaurus):  # pylint: disable=no-value-for-parameter
            reindex_object(event.object, thesaurus.catalog)


@subscriber(IObjectRemovedEvent, context_selector=IThesaurusTerm)
def handle_removed_term(event):
    """Un-index term into inner catalog"""
    parent = event.oldParent
    if IThesaurusTermsContainer.providedBy(parent):  # pylint: disable=no-value-for-parameter
        thesaurus = parent.__parent__
        if IThesaurus.providedBy(thesaurus):  # pylint: disable=no-value-for-parameter
            unindex_object(event.object, thesaurus.catalog)


@adapter_config(required=IThesaurusTerm, provides=INode)
class ThesaurusTermTreeAdapter(ContextAdapter):
    """Thesaurus term tree node adapter"""

    @property
    def label(self):
        """Label getter"""
        return self.context.label

    @property
    def css_class(self):
        """CSS class getter"""
        return self.context.status

    @property
    def order(self):
        """Order getter"""
        return self.context.order or 999

    def get_level(self):
        """Level getter"""
        return self.context.level

    def has_children(self, filter_value=None):
        """Children checker"""
        specifics = self.context.specifics
        if filter_value:
            specifics = list(filter(lambda x: filter_value in (x.extracts or ()), specifics))
        return len(specifics) > 0

    def get_children(self, filter_value=None):  # pylint: disable=unused-argument
        """Children getter"""
        return self.context.specifics


@adapter_config(required=IThesaurusTerm, provides=IViewContextPermissionChecker)
class ThesaurusTermPermissionChecker(ContextAdapter):
    """Thesaurus term permission checker"""

    edit_permission = MANAGE_THESAURUS_CONTENT_PERMISSION


@vocabulary_config(name=THESAURUS_EXTENSIONS_VOCABULARY)
class ThesaurusTermExtensionsVocabulary(SimpleVocabulary):
    """Thesaurus term extensions vocabulary"""

    interface = IThesaurusTermExtension

    def __init__(self, context=None):  # pylint: disable=unused-argument
        registry = get_pyramid_registry()
        translate = check_request().localizer.translate
        try:
            terms = [
                SimpleTerm(name, title=translate(util.label))
                for name, util in registry.getUtilitiesFor(self.interface)
            ]
        except ComponentLookupError:
            terms = []
        super().__init__(terms)
