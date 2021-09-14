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

"""PyAMS_thesaurus.schema module

This module defines schemas interfaces and fields used o store thesaurus terms.
"""

from zope.interface import Interface, implementer
from zope.schema import Choice, List, Object, Set, TextLine
from zope.schema.interfaces import IList, IObject, SchemaNotProvided


__docformat__ = 'restructuredtext'


class IThesaurusTermField(IObject):
    """Marker interface to define a thesaurus term field"""

    thesaurus_name = TextLine(title="Thesaurus name",
                              required=False)

    extract_name = TextLine(title="Extract name",
                            required=False)


class IThesaurusTermsListField(IList):
    """Marker interface to define a list of thesaurus terms"""

    thesaurus_name = TextLine(title="Thesaurus name",
                              required=False)

    extract_name = TextLine(title="Extract name",
                            required=False)


@implementer(IThesaurusTermField)
class ThesaurusTermField(Object):
    """Thesaurus term schema field"""

    def __init__(self, schema=None, thesaurus_name='', extract_name='', **kw):
        super().__init__(schema=Interface, **kw)
        self.thesaurus_name = thesaurus_name
        self.extract_name = extract_name

    def _validate(self, value):
        super()._validate(value)
        # schema has to be provided by value
        if not self.schema.providedBy(value):
            raise SchemaNotProvided


@implementer(IThesaurusTermsListField)
class ThesaurusTermsListField(List):
    """Thesaurus terms list schema field"""

    def __init__(self, value_type=None, unique=False, thesaurus_name='', extract_name='', **kw):
        super().__init__(value_type=Object(schema=Interface), unique=False, **kw)
        self.thesaurus_name = thesaurus_name
        self.extract_name = extract_name


class ValidatedSet(Set):
    """A set field validated when not bound to a context"""

    def _validate(self, value):
        # Don't try to validate with empty context !
        if self.context is None:
            return
        super()._validate(value)


class ValidatedChoice(Choice):
    """An always validated choice field"""

    def _validate(self, value):
        """Don't need to validate!"""
