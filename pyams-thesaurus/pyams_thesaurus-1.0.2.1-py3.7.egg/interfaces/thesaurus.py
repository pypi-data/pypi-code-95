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

"""PyAMS_thesaurus.interfaces.thesaurus module

This module defines thesaurus utility interfaces.
"""

from hypatia.interfaces import ICatalog
from zope.annotation import IAttributeAnnotatable
from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.interface import Attribute, Interface
from zope.location.interfaces import IContained
from zope.schema import Bool, Choice, Date, List, Object, Text, TextLine

from pyams_i18n.interfaces import BASE_LANGUAGES_VOCABULARY_NAME
from pyams_security.schema import PrincipalsSetField
from pyams_thesaurus.interfaces import THESAURUS_ADMIN_ROLE, THESAURUS_EXTRACTS_VOCABULARY, \
    THESAURUS_EXTRACT_MANAGER_ROLE, THESAURUS_MANAGER_ROLE, THESAURUS_NAMES_VOCABULARY
from pyams_thesaurus.interfaces.term import IThesaurusTerm
from pyams_utils.schema import ColorField


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


class IThesaurusDescription(Interface):
    """Thesaurus base info"""

    title = TextLine(title=_("Title"),
                     description=_("Long title for this thesaurus"),
                     required=False)

    subject = TextLine(title=_("Subject"),
                       required=False)

    description = Text(title=_("Description"),
                       required=False)

    language = Choice(title=_("Language"),
                      description=_("Thesaurus's language"),
                      required=False,
                      default='en',
                      vocabulary=BASE_LANGUAGES_VOCABULARY_NAME)

    creator = TextLine(title=_("Creator"),
                       required=False)

    publisher = TextLine(title=_("Publisher"),
                         required=False)

    created = Date(title=_("Creation date"),
                   required=False)


class IThesaurusInfo(IThesaurusDescription):
    """Thesaurus base info"""

    name = TextLine(title=_("Thesaurus name"),
                    required=True)

    terms = Attribute("Thesaurus terms")

    top_terms = List(title=_("Thesaurus top-terms"),
                     description=_("List of top thesaurus terms, placed at first level"),
                     required=False,
                     value_type=Object(schema=IThesaurusTerm))

    catalog = Object(title=_("Thesaurus catalog"),
                     description=_("Inner thesaurus catalog, used for full-text indexing"),
                     schema=ICatalog)

    def init_catalog(self):
        """Initialize thesaurus catalog"""

    def load(self, configuration):
        """Load contents from given configuration"""

    def merge(self, configuration, thesaurus=None):
        """Merge current thesaurus with another one for given configuration"""

    def reset_terms_parent(self):
        """Reset thesaurus terms parent attribute"""

    def get_top_terms(self, extract=None):
        """Get top terms, for given extract or for the whole thesaurus"""

    def reset_top_terms(self):
        """Reset thesaurus top terms"""

    def clear(self):
        """Clear thesaurus contents"""

    def find_terms(self, query=None, extract=None, glob='end', limit=None,  # pylint: disable=too-many-arguments
                   exact=False, exact_only=False, stemmed=False):
        """Get terms matching given query and parent

        @param query: the text query
        @param extract: selected extract name, if any
        @param glob: can be 'start' (default), 'end', 'both' or None to handle globs
        @param limit: maximum number of search results
        @param exact: if True, terms exactly matching query will be returned
        @param exact_only: if False, stemmed query will also be executed
        @param stemmed: if True, query will use stemmed words
        """

    def get_nodes(self, term, result, subnodes=None, request=None):
        """Get tree nodes matching given term

        @param term: parent term
        @param result: output result from previous nodes, as method can be called recursively
        @param subnodes:
        """

    def delete(self):
        """Delete thesaurus"""


class IThesaurusRoles(Interface):
    """Thesaurus roles interface"""

    administrators = PrincipalsSetField(title=_("Administrators"),
                                        description=_("List of thesaurus's administrators"),
                                        role_id=THESAURUS_ADMIN_ROLE,
                                        required=False)

    managers = PrincipalsSetField(title=_("Contents managers"),
                                  description=_("List of thesaurus's contents contributors"),
                                  role_id=THESAURUS_MANAGER_ROLE,
                                  required=False)


class IThesaurus(IThesaurusInfo, IContained, IAttributeAnnotatable):
    """Thesaurus interface"""


THESAURUS_MANAGER_NAME = 'Thesaurus'


class IThesaurusManager(IContainer):
    """Thesaurus container utility interface"""

    contains(IThesaurus)

    root_menu = Bool(title=_("Access menu from home"),
                     description=_("If 'yes', a menu will be displayed to get access to "
                                   "thesaurus from site admin root"),
                     required=True,
                     default=False)


class IThesaurusManagerTarget(Interface):
    """Marker interface for contents managing thesaurus"""


class IThesaurusTarget(Interface):
    """Marker interface for contents indexed on a thesaurus base"""


#
# Thesaurus extracts interfaces
#

class IThesaurusExtractInfo(Interface):
    """Thesaurus extract base info"""

    name = TextLine(title=_("Extract name"),
                    required=True)

    description = Text(title=_("Description"),
                       required=False)

    abbreviation = TextLine(title=_("Abbreviation"),
                            description=_("Short abbreviation used to distinguish the extract"),
                            required=True,
                            max_length=3)

    color = ColorField(title=_("Extract color"),
                       description=_("A color associated with this extract"),
                       required=True)

    def add_term(self, term):
        """Add a term to this extract"""

    def remove_term(self, term):
        """Remove a term from this extract"""

    def get_nodes(self, term, result, subnodes=None, request=None):
        """Extract terms getter"""


class IThesaurusExtractRoles(Interface):
    """Thesaurus extract roles"""

    managers = PrincipalsSetField(title=_("Extract managers"),
                                  description=_("List of principals which can manage extract "
                                                "contents"),
                                  role_id=THESAURUS_EXTRACT_MANAGER_ROLE,
                                  required=False)


class IThesaurusExtract(IThesaurusExtractInfo, IAttributeAnnotatable):
    """Thesaurus extract info"""


class IThesaurusExtracts(IContainer):
    """Thesaurus extracts container interface"""

    contains(IThesaurusExtractInfo)


class IThesaurusContextManager(Interface):
    """Thesaurus terms manager interface"""

    thesaurus_name = Choice(title=_("Thesaurus name"),
                            vocabulary=THESAURUS_NAMES_VOCABULARY,
                            required=False)

    extract_name = Choice(title=_("Thesaurus extract"),
                          vocabulary=THESAURUS_EXTRACTS_VOCABULARY,
                          required=False)


class IThesaurusContextManagerTarget(Interface):
    """Marker interface for tools managing thesaurus terms"""
