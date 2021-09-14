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

"""PyAMS_thesaurus.thesaurus module

This module define thesaurus utility class.
"""

import re

from hypatia.catalog import Catalog
from hypatia.query import Contains, Eq
from hypatia.text import Lexicon
from hypatia.text.parsetree import QueryError
from persistent import Persistent
from pyramid.events import subscriber
from transaction.interfaces import ITransactionManager
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.interface import implementer
from zope.lifecycleevent import IObjectAddedEvent, IObjectRemovedEvent
from zope.location import locate
from zope.location.interfaces import ISublocations
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable

from pyams_catalog.index import FieldIndexWithInterface, TextIndexWithInterface
from pyams_catalog.nltk import NltkStemmedTextProcessor
from pyams_catalog.query import CatalogResultSet, or_
from pyams_catalog.utils import index_object
from pyams_security.interfaces import IDefaultProtectionPolicy, IRolesPolicy, \
    IViewContextPermissionChecker
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_site.interfaces import ISiteRoot
from pyams_thesaurus.interfaces import ADMIN_THESAURUS_PERMISSION, \
    THESAURUS_EXTRACTS_VOCABULARY, THESAURUS_NAMES_VOCABULARY, THESAURUS_VOCABULARY
from pyams_thesaurus.interfaces.extension import IThesaurusTermExtension
from pyams_thesaurus.interfaces.loader import IThesaurusLoader
from pyams_thesaurus.interfaces.term import IThesaurusLoaderTerm, IThesaurusTerm, \
    IThesaurusTermsContainer
from pyams_thesaurus.interfaces.thesaurus import IThesaurus, IThesaurusContextManager, \
    IThesaurusExtract, IThesaurusExtractRoles, IThesaurusExtracts, IThesaurusRoles
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.interfaces.tree import INode, ITree
from pyams_utils.registry import query_utility
from pyams_utils.request import check_request
from pyams_utils.traversing import get_parent
from pyams_utils.unicode import translate_string
from pyams_utils.url import absolute_url
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'

from pyams_zmi.interfaces import IObjectLabel


CUSTOM_SEARCH = re.compile(r'\*|\"|\sand\s|\sor\s|\snot\s|\(|\)', re.IGNORECASE)


@implementer(IThesaurusTermsContainer)
class ThesaurusTermsContainer(BTreeContainer):
    """Thesaurus terms container"""

    def clear(self):
        """Terms container clear"""
        self._SampleContainer__data.clear()
        self._BTreeContainer__len.set(0)  # pylint: disable=no-member


@factory_config(IThesaurus)  # pylint: disable=too-many-instance-attributes
@implementer(ISublocations, IDefaultProtectionPolicy)
class Thesaurus(ProtectedObjectMixin, Persistent, Contained):
    """Thesaurus persistent class"""

    name = FieldProperty(IThesaurus['name'])
    title = FieldProperty(IThesaurus['title'])
    subject = FieldProperty(IThesaurus['subject'])
    description = FieldProperty(IThesaurus['description'])
    language = FieldProperty(IThesaurus['language'])
    creator = FieldProperty(IThesaurus['creator'])
    publisher = FieldProperty(IThesaurus['publisher'])
    created = FieldProperty(IThesaurus['created'])

    terms = None
    _top_terms = FieldProperty(IThesaurus['top_terms'])

    catalog = FieldProperty(IThesaurus['catalog'])

    def __init__(self, name=None, description=None, terms=None):
        if name:
            self.name = name
        if description:
            self.title = description.title
            self.subject = description.subject
            self.description = description.description
            self.language = description.language
            self.creator = description.creator
            self.publisher = description.publisher
            self.created = description.created
        if not IThesaurusTermsContainer.providedBy(terms):  # pylint: disable=no-value-for-parameter
            terms = ThesaurusTermsContainer()
        self.terms = terms
        locate(terms, self, '++terms++')
        self.reset_terms_parent()
        self.reset_top_terms()

    def sublocations(self):
        """Sub-locations getter"""
        yield from (self.terms, self.catalog)

    @property
    def top_terms(self):
        """Top terms getter"""
        return self._top_terms

    @top_terms.setter
    def top_terms(self, value):
        """Top terms setter"""
        self._top_terms = [term for term in value or () if term.usage is None]

    def init_catalog(self):
        """Inner catalog initialization"""
        # Init catalog
        catalog = self.catalog = Catalog()
        locate(catalog, self)
        # Init fulltext search catalog
        catalog['fulltext'] = TextIndexWithInterface(IThesaurusTerm, 'label',
                                                     language=self.language)
        # Init stemmed search catalog
        catalog['stemmed'] = TextIndexWithInterface(IThesaurusTerm, 'label',
                                                    lexicon=Lexicon(NltkStemmedTextProcessor(
                                                        language=self.language)))
        # Init value search catalog
        catalog['value'] = FieldIndexWithInterface(IThesaurusTerm, 'base_label')
        for idx, term in enumerate(self.terms.values()):
            index_object(term, catalog)
            if not idx % 100:
                try:
                    ITransactionManager(catalog).savepoint()
                except TypeError:
                    # Can fail if thesaurus is not stored yet...
                    pass

    def load(self, configuration):
        """Load terms from given configuration"""
        loader = query_utility(IThesaurusLoader, name=configuration.format)
        if loader is not None:
            result = loader.load(configuration.data, configuration)
            self.merge(configuration, result)

    def merge(self, configuration, thesaurus=None):
        """Merge existing thesaurus terms with imported configuration"""
        if thesaurus is None:
            loader = query_utility(IThesaurusLoader, name=configuration.format)
            if loader is not None:
                thesaurus = loader.load(configuration.data)
        if thesaurus is not None:
            # define or merge items from given thesaurus
            terms = self.terms
            for idx, (key, term) in enumerate(thesaurus.terms.items()):
                # check for term conflict
                suffix = getattr(configuration, 'conflict_suffix', None)
                if suffix:
                    suffixed_key = key + ' ' + suffix
                    if suffixed_key in terms:
                        key = suffixed_key
                    elif key in terms:
                        term.label = key
                if key in terms:
                    terms[key].merge(term, configuration)
                elif not IThesaurusLoaderTerm.providedBy(term):  # pylint: disable=no-value-for-parameter
                    terms[key] = term
                if not idx % 100:
                    try:
                        ITransactionManager(self).savepoint()
                    except TypeError:
                        # Can fail if thesaurus is not stored yet...
                        pass
        self.reset_terms_parent()
        self.reset_top_terms()

    def reset_terms_parent(self):
        """Reset parent from thesaurus terms"""
        for idx, term in enumerate(self.terms.values()):
            # reset generic/specifics attributes
            generic = term.generic
            if (generic is not None) and (term not in generic.specifics):
                generic.specifics = generic.specifics + [term, ]
            # reset term's first level parent
            parent = term
            while parent.generic is not None:
                parent = parent.generic
            term.parent = parent
            if not idx % 100:
                try:
                    ITransactionManager(self).savepoint()
                except TypeError:
                    # Can fail if thesaurus is not stored yet...
                    pass

    def reset_top_terms(self):
        """Reset thesaurus top terms"""
        self.top_terms = [
            term for term in self.terms.values()
            if (not term.generic) and (not term.usage)
        ]

    def get_top_terms(self, extract=None):
        """Get thesaurus top terms"""
        if not extract:
            return self.top_terms
        return [term for term in self.top_terms if extract in term.extracts]

    def clear(self):
        """Remove all terms from thesaurus"""
        self.terms.clear()
        self.catalog.reset()
        self.top_terms = []

    def find_terms(self, query=None, extract=None, glob='end', limit=None,  # pylint: disable=too-many-arguments
                   exact=False, exact_only=False, stemmed=False):
        """Find terms matching given criteria"""
        assert exact or (not exact_only)
        terms = []
        if exact:
            query_text = translate_string(query, escape_slashes=True,
                                          force_lower=True, spaces=' ')
            terms = list(CatalogResultSet(Eq(self.catalog['value'], query_text)))
        if not exact_only:
            search = None
            # check stemmed index
            if stemmed and not re.search(r'\*', query):
                search = Contains(self.catalog['stemmed'],
                                  ' and '.join(m
                                               for m in query.split()
                                               if len(m) > 2))
            # check basic index
            start = ''
            end = ''
            if CUSTOM_SEARCH.search(query):
                query_text = query
            else:
                if glob in ('start', 'both'):
                    # Starting glob is not supported!!
                    start = ''
                if glob in ('end', 'both'):
                    end = '*'
                query_text = ' and '.join((
                    '{start}{mid}{end}'.format(start=start, mid=m, end=end)
                    for m in query.split()
                    if len(m) > 2
                ))
            search = or_(search, Contains(self.catalog['fulltext'], query_text))
            try:
                terms += sorted(CatalogResultSet(search.execute()),
                                key=lambda x: x.label)
            except QueryError:
                pass
        if extract:
            terms = filter(lambda term: extract in term.extracts, terms)
        if limit:
            terms = terms[:limit]
        return terms

    def get_nodes(self, term, result, subnodes=None, request=None):
        """Get nodes matching given parent term"""
        if request is None:
            request = check_request()
        registry = request.registry
        translate = request.localizer.translate
        extracts = IThesaurusExtracts(self)
        for child in INode(term).get_children():
            node = INode(child)
            result.append({
                'label': node.label.replace("'", "&#039;"),
                'view': absolute_url(node.context, request, 'properties.html'),
                'css_class': node.css_class,
                'extracts': [
                    {
                        'name': name,
                        'title': extract.name,
                        'color': extract.color,
                        'used': name in (node.context.extracts or ())
                    }
                    for name, extract in sorted(extracts.items(), key=lambda x: x[0])
                ],
                'extensions': [
                    {
                        'name': name,
                        'title': translate(ext.label),
                        'icon': ext.icon_css_class,
                        'view': absolute_url(node.context, request, ext.target_view),
                        'active': name in node.context.extensions
                    }
                    for name, ext in sorted(registry.getUtilitiesFor(IThesaurusTermExtension),
                                            key=lambda ext: ext[1].weight,
                                            reverse=True)
                ],
                'expand': node.has_children()
            })
            if subnodes and (node.context.label in subnodes):
                nodes = result[-1]['subnodes'] = []
                self.get_nodes(node.context, nodes, subnodes, request)

    def delete(self):
        """Delete thesaurus"""


@adapter_config(required=IThesaurus,
                provides=IObjectLabel)
def thesaurus_label(context):
    """Thesaurus label getter"""
    return context.name


@implementer(IThesaurusRoles)
class ThesaurusRoles(ProtectedObjectRoles):
    """Thesaurus roles"""

    administrators = RolePrincipalsFieldProperty(IThesaurusRoles['administrators'])
    managers = RolePrincipalsFieldProperty(IThesaurusRoles['managers'])


@adapter_config(required=IThesaurus,
                provides=IThesaurusRoles)
def thesaurus_roles_adapter(context):
    """Thesaurus roles adapter"""
    return ThesaurusRoles(context)


@adapter_config(name='thesaurus_roles',
                required=IThesaurus,
                provides=IRolesPolicy)
class ThesaurusRolesPolicy(ContextAdapter):
    """Thesaurus roles policy"""

    roles_interface = IThesaurusRoles
    weight = 20


@subscriber(IObjectAddedEvent, context_selector=IThesaurus)
def handle_added_thesaurus(event):
    """Handle added thesaurus to init inner catalog"""
    sm = get_parent(event.newParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        thesaurus = event.object
        sm.getSiteManager().registerUtility(event.object, IThesaurus,
                                            name=thesaurus.name or '')
        thesaurus.init_catalog()


@subscriber(IObjectRemovedEvent, context_selector=IThesaurus)
def handle_removed_thesaurus(event):
    """Handle removed thesaurus"""
    sm = get_parent(event.oldParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        thesaurus = event.object
        sm.getSiteManager().registerUtility(event.object, IThesaurus,
                                            name=thesaurus.name or '')


@adapter_config(required=IThesaurus,
                provides=IViewContextPermissionChecker)
class ThesaurusPermissionChecker(ContextAdapter):
    """Thesaurus edit permission checker"""

    edit_permission = ADMIN_THESAURUS_PERMISSION


@adapter_config(required=IThesaurus,
                provides=ITree)
class ThesaurusTreeAdapter(ContextAdapter):
    """Thesaurus tree adapter"""

    def get_root_nodes(self):
        """Thesaurus root nodes getter"""
        return sorted(self.context.top_terms, key=lambda x: (x.order or 999, x.label))


#
# Thesaurus extracts
#

THESAURUS_EXTRACTS_KEY = 'pyams_thesaurus.extracts'


@factory_config(IThesaurusExtracts)
class ThesaurusExtractsContainer(BTreeContainer):
    """Thesaurus extracts container"""


@adapter_config(required=IThesaurus,
                provides=IThesaurusExtracts)
def thesaurus_extracts_factory(context):
    """Thesaurus extracts factory"""
    return get_annotation_adapter(context, THESAURUS_EXTRACTS_KEY, IThesaurusExtracts,
                                  name='++extracts++')


@adapter_config(name='extracts',
                required=IThesaurus,
                provides=ITraversable)
class ThesaurusExtractsNamespace(ContextAdapter):
    """Thesaurus ++extracts++ namespace"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Thesaurus extracts traverse"""
        extracts = IThesaurusExtracts(self.context)
        if name:
            return extracts[name]
        return extracts


@factory_config(IThesaurusExtract)
@implementer(IDefaultProtectionPolicy)
class ThesaurusExtract(ProtectedObjectMixin, Persistent, Contained):
    """Thesaurus extract"""

    name = FieldProperty(IThesaurusExtract['name'])
    description = FieldProperty(IThesaurusExtract['description'])
    abbreviation = FieldProperty(IThesaurusExtract['abbreviation'])
    color = FieldProperty(IThesaurusExtract['color'])

    def add_term(self, term):
        """Add term to extract"""
        term.add_extract(self)

    def remove_term(self, term):
        """Remove term from extract"""
        term.remove_extract(self)

    def get_nodes(self, term, result, subnodes=None, request=None):
        """Extract nodes getter"""
        if request is None:
            request = check_request()
        extract_name = self.name
        for child in INode(term).get_children():
            node = INode(child)
            if extract_name in (node.context.extracts or ()):
                result.append({
                    'label': node.label.replace("'", "&#039;"),
                    'view': absolute_url(node.context, request, 'properties.html'),
                    'css_class': node.css_class,
                    'extracts': [],
                    'extensions': [],
                    'expand': node.has_children(extract_name)
                })
                if subnodes and (node.context.label in subnodes):
                    nodes = result[-1]['subnodes'] = []
                    self.get_nodes(node.context, nodes, subnodes, request)


@adapter_config(required=IThesaurusExtract,
                provides=IViewContextPermissionChecker)
class ThesaurusExtractPermissionChecker(ContextAdapter):
    """Thesaurus extract permission checker"""

    edit_permission = ADMIN_THESAURUS_PERMISSION


@implementer(IThesaurusExtractRoles)
class ThesaurusExtractRoles(ProtectedObjectRoles):
    """Thesaurus extract roles"""

    managers = RolePrincipalsFieldProperty(IThesaurusExtractRoles['managers'])


@adapter_config(required=IThesaurusExtract,
                provides=IThesaurusExtractRoles)
def thesaurus_extract_roles_adapter(context):
    """Thesaurus extract roles adapter"""
    return ThesaurusExtractRoles(context)


@adapter_config(name='thesaurus_extract_roles',
                required=IThesaurusExtract,
                provides=IRolesPolicy)
class ThesaurusExtractRolesPolicy(ContextAdapter):
    """Thesaurus extract roles policy"""

    roles_interface = IThesaurusExtractRoles
    weight = 20


@subscriber(IObjectRemovedEvent, context_selector=IThesaurusExtract)
def handle_removed_extract(event):
    """Handle removed extract"""
    thesaurus = get_parent(event.object, IThesaurus)
    name = event.object.name
    for term in thesaurus.terms.values():
        term.remove_extract(name, check=False)


#
# Vocabularies
#

@vocabulary_config(name=THESAURUS_VOCABULARY)
class ThesaurusVocabulary(UtilityVocabulary):
    """Thesaurus utilities vocabulary"""

    interface = IThesaurus
    nameOnly = False


@vocabulary_config(name=THESAURUS_NAMES_VOCABULARY)
class ThesaurusNamesVocabulary(UtilityVocabulary):
    """Thesaurus names utilities vocabulary"""

    interface = IThesaurus
    nameOnly = True


@vocabulary_config(name=THESAURUS_EXTRACTS_VOCABULARY)
class ThesaurusExtractsVocabulary(SimpleVocabulary):
    """Thesaurus extracts vocabulary"""

    def __init__(self, context=None):
        terms = []
        if context is not None:
            request = check_request()
            thesaurus_name = request.headers.get('X-Thesaurus-Name')
            if thesaurus_name is not None:
                thesaurus = query_utility(IThesaurus, name=thesaurus_name)
            else:
                thesaurus = get_parent(context, IThesaurus)
                if thesaurus is None:
                    context_manager = IThesaurusContextManager(context, None)
                    if (context_manager is not None) and context_manager.thesaurus_name:
                        thesaurus = query_utility(IThesaurus,
                                                  name=context_manager.thesaurus_name)
            if thesaurus is not None:
                extracts = IThesaurusExtracts(thesaurus)
                terms = [
                    SimpleTerm(extract.__name__, title=extract.name)
                    for extract in extracts.values()
                ]
                terms.sort(key=lambda x: x.title)
        super().__init__(terms)
