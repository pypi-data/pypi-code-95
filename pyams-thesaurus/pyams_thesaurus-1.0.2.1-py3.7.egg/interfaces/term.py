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

"""PyAMS_thesaurus.interfaces.term module

This module defines thesaurus terms interfaces.
"""

from zope.container.interfaces import IContainer
from zope.interface import Attribute, Interface, Invalid, invariant
from zope.location.interfaces import IContained
from zope.schema import Bool, Choice, Datetime, Int, Set, Text, TextLine
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_thesaurus.interfaces.extension import THESAURUS_EXTENSIONS_VOCABULARY
from pyams_thesaurus.interfaces import THESAURUS_EXTRACTS_VOCABULARY
from pyams_thesaurus.schema import ThesaurusTermField, ThesaurusTermsListField, ValidatedSet


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _


STATUS_CANDIDATE = 'candidate'
STATUS_PUBLISHED = 'published'
STATUS_ARCHIVED = 'archived'

THESAURUS_STATUS = (STATUS_CANDIDATE,
                    STATUS_PUBLISHED,
                    STATUS_ARCHIVED)

THESAURUS_STATUS_LABELS = (_("Candidate"),
                           _("Published"),
                           _("Archived"))

THESAURUS_STATUS_VOCABULARY = SimpleVocabulary([
    SimpleTerm(THESAURUS_STATUS[i], t, t)
    for i, t in enumerate(THESAURUS_STATUS_LABELS)
])


class IThesaurusTerm(IContained):
    """Thesaurus term base interface"""

    id = Attribute("Internal ID")

    label = TextLine(title=_("Term label"),
                     description=_("Full keyword for the given term"),
                     required=True)

    @invariant
    def check_label(self):
        """Check label for forbidden characters"""
        if '/' in self.label:  # pylint: disable=unsupported-membership-test
            raise Invalid(_("'/' character is forbidden in term's label"))

    base_label = Attribute("Base label without uppercase or accentuated character")

    title = Attribute("Term external title")

    alt = TextLine(title=_("Alternate label"),
                   description=_("Not to be confused with synonyms 'usage' label, given "
                                 "below..."),
                   required=False)

    definition = Text(title=_("Definition"),
                      description=_("Long definition, mostly for complicated terms"),
                      required=False)

    note = Text(title=_("Term's application note"),
                description=_("Application note for the given term"),
                required=False)

    generic = ThesaurusTermField(title=_("Generic term"),
                                 description=_("Parent generic term of the current term"),
                                 required=False)

    order = Int(title=_("Order"),
                description=_("Term's position between it's siblings; default terms order "
                              "is alphabetical"),
                required=False)

    specifics = ThesaurusTermsListField(title=_("Specifics terms"),
                                        description=_("Child more specifics terms of the "
                                                      "current term"),
                                        required=False)

    associations = ThesaurusTermsListField(title=_("Associated terms"),
                                           description=_("Other terms associated to the "
                                                         "current term"),
                                           required=False)

    usage = ThesaurusTermField(title=_("Usage"),
                               description=_("For synonyms, specify here the term's descriptor "
                                             "to use"),
                               required=False)

    used_for = ThesaurusTermsListField(title=_("Synonyms"),
                                       description=_("For a given allowed descriptor, specify "
                                                     "here the list of synonyms"),
                                       required=False)

    @invariant
    def check_synonym(self):
        """Check term for synonyms"""
        if self.usage is not None:
            if self.generic is not None:
                raise Invalid(_("A term can't be a synonym and attached to a generic term"))
            if self.used_for:
                raise Invalid(_("A term used as synonym can't have it's own synonyms "
                                "(all synonyms should be attached to the descriptor)"))

    extracts = ValidatedSet(title=_("Extracts"),
                            description=_("List of thesaurus extracts including this term"),
                            required=False,
                            value_type=Choice(vocabulary=THESAURUS_EXTRACTS_VOCABULARY))

    extensions = Set(title=_("Extensions"),
                     description=_("List of available extensions applied to this term"),
                     required=False,
                     value_type=Choice(vocabulary=THESAURUS_EXTENSIONS_VOCABULARY))

    status = Choice(title=_("Status"),
                    description=_("Term status"),
                    required=True,
                    vocabulary=THESAURUS_STATUS_VOCABULARY,
                    default='published')

    level = Attribute("Term's level in the thesaurus tree")

    micro_thesaurus = Bool(title=_("Micro-thesaurus?"),
                           description=_("Is the term part of a micro-thesaurus?"),
                           required=False)

    parent = ThesaurusTermField(title=_("First level parent"),
                                description=_("Parent at level 1 of the current term, or None"),
                                required=False,
                                schema=Interface)

    created = Datetime(title=_("Creation date"),
                       required=False)

    modified = Datetime(title=_("Modification date"),
                        required=False)

    def add_extract(self, extract, check=True):
        """Add given extract to the list of term extracts"""

    def remove_extract(self, extract, check=True):
        """Remove given extract from the list of term extracts"""

    def query_extensions(self):
        """Get list of extension utilities"""

    def get_parents(self):
        """Get list of term's parents"""

    def get_siblings(self):
        """Get siblings of current term"""

    def get_all_children(self, terms=None, with_synonyms=False):
        """Get full list of term's specifics"""

    def merge(self, term, configuration):
        """Merge term attributes with given term, to avoid overwriting all entity"""


IThesaurusTerm['generic'].schema = IThesaurusTerm
IThesaurusTerm['usage'].schema = IThesaurusTerm
IThesaurusTerm['parent'].schema = IThesaurusTerm


class IThesaurusLoaderTerm(Interface):
    """Marker interface for temporary thesaurus loader terms"""


class IThesaurusTermsContainer(IContainer):
    """Thesaurus terms container interface"""
