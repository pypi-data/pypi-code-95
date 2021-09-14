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

"""PyAMS_thesaurus.loader main module

This module defines common thesaurus loaders components and base classes.
"""

from datetime import datetime
from tempfile import TemporaryFile

from BTrees.OOBTree import OOBTree  # pylint: disable=no-name-in-module,import-error
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.interface import alsoProvides, implementer, noLongerProvides
from zope.schema.fieldproperty import FieldProperty

from pyams_thesaurus.interfaces.loader import IThesaurusExporter, IThesaurusExporterHandler, \
    IThesaurusLoader, IThesaurusLoaderHandler, THESAURUS_EXPORTERS_VOCABULARY, \
    THESAURUS_LOADERS_VOCABULARY
from pyams_thesaurus.interfaces.term import IThesaurusLoaderTerm
from pyams_thesaurus.interfaces.thesaurus import IThesaurusDescription
from pyams_thesaurus.term import ThesaurusTerm
from pyams_thesaurus.thesaurus import Thesaurus, ThesaurusTermsContainer
from pyams_utils.request import query_request
from pyams_utils.unicode import translate_string
from pyams_utils.vocabulary import vocabulary_config


__docformat__ = 'restructuredtext'


#
# Thesaurus loader classes
#

@implementer(IThesaurusDescription)
class ThesaurusLoaderDescription:
    """Thesaurus loader description"""

    title = FieldProperty(IThesaurusDescription['title'])
    subject = FieldProperty(IThesaurusDescription['subject'])
    description = FieldProperty(IThesaurusDescription['description'])
    language = FieldProperty(IThesaurusDescription['language'])
    creator = FieldProperty(IThesaurusDescription['creator'])
    publisher = FieldProperty(IThesaurusDescription['publisher'])
    _created = FieldProperty(IThesaurusDescription['created'])

    @property
    def created(self):
        """Creation date getter"""
        return self._created

    @created.setter
    def created(self, value):
        """Creation date setter"""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                value = datetime.today().date()
        self._created = value


class ThesaurusLoaderTerm:  # pylint: disable=too-many-instance-attributes
    """Thesaurus loader term"""

    def __init__(self, label, alt=None, definition=None, note=None,  # pylint: disable=too-many-arguments
                 generic=None, specifics=None, associations=None,
                 usage=None, used_for=None, created=None, modified=None,
                 weight=0, properties=None):
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
        self.weight = int(weight)
        self.properties = properties or {}


@implementer(IThesaurusLoaderHandler)
class BaseThesaurusLoaderHandler:
    """Base thesaurus loader handler"""

    def __init__(self, configuration):
        self.configuration = configuration


class XMLThesaurusLoaderHandler(BaseThesaurusLoaderHandler):
    """Base XML thesaurus loader handler"""


@implementer(IThesaurusLoader)
class BaseThesaurusLoader:
    """Base thesaurus loader"""

    handler = None

    def load(self, data, configuration=None):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """Terms loader"""
        handler = self.handler(configuration)  # pylint: disable=not-callable
        if isinstance(data, tuple):
            data = data[1]
        if hasattr(data, 'seek'):
            data.seek(0)
        description, terms = handler.read(data, configuration)
        if configuration and configuration.language and not description.language:
            description.language = configuration.language
        key_store = OOBTree()
        store = ThesaurusTermsContainer()
        # first loop to initialize terms
        for key, term in terms.items():
            new_term = ThesaurusTerm(label=term.label,
                                     alt=term.alt,
                                     definition=term.definition,
                                     note=term.note,
                                     created=term.created,
                                     modified=term.modified)
            alsoProvides(new_term, IThesaurusLoaderTerm)
            key_store[key] = store[term.label] = new_term
            noLongerProvides(new_term, IThesaurusLoaderTerm)
        # second loop to update terms links
        for key, term in terms.items():
            new_term = key_store[key]
            # check generic term
            if term.generic:
                target = key_store.get(term.generic)
                if target is None:
                    target = ThesaurusTerm(label=term.generic)
                    alsoProvides(target, IThesaurusLoaderTerm)
                    key_store[target.label] = store[target.label] = target
                new_term.generic = target
            # check specific terms
            if term.specifics:
                for specific in term.specifics:
                    if key_store.get(specific) is None:
                        target = ThesaurusTerm(label=specific)
                        alsoProvides(target, IThesaurusLoaderTerm)
                        key_store[target.label] = store[target.label] = target
                new_term.specifics = [
                    key_store.get(specific)
                    for specific in term.specifics
                ]
                for subterm in new_term.specifics:
                    subterm.generic = new_term
            # check associations
            if term.associations:
                for association in term.associations:
                    if key_store.get(association) is None:
                        target = ThesaurusTerm(label=association)
                        alsoProvides(target, IThesaurusLoaderTerm)
                        key_store[target.label] = store[target.label] = target
                new_term.associations = [
                    key_store.get(association)
                    for association in term.associations
                ]
            # check usage term
            if term.usage:
                target = key_store.get(term.usage)
                if target is None:
                    target = ThesaurusTerm(label=term.usage)
                    alsoProvides(target, IThesaurusLoaderTerm)
                    key_store[target.label] = store[target.label] = target
                new_term.usage = target
                target.used_for = set(target.used_for) | {new_term}
            # check used-for term
            if term.used_for:
                for used in term.used_for:
                    if key_store.get(used) is None:
                        target = ThesaurusTerm(label=used)
                        alsoProvides(target, IThesaurusLoaderTerm)
                        key_store[target.label] = store[target.label] = target
                new_term.used_for = [
                    key_store.get(used)
                    for used in term.used_for
                ]
                for synonym in new_term.used_for:
                    synonym.usage = new_term
        return Thesaurus(description=description, terms=store)


@vocabulary_config(name=THESAURUS_LOADERS_VOCABULARY)
class ThesaurusLoadersVocabulary(UtilityVocabulary):
    """Thesaurus loaders vocabulary"""

    interface = IThesaurusLoader
    nameOnly = True


#
# Thesaurus exporters classes
#

@implementer(IThesaurusExporterHandler)
class BaseThesaurusExporterHandler:
    """Base thesaurus exporter handler"""

    content_type = None

    def __init__(self, configuration):
        self.configuration = configuration


class XMLThesaurusExporterHandler(BaseThesaurusExporterHandler):
    """Base XML thesaurus exporter handler"""

    content_type = 'text/xml'

    def _write(self, thesaurus, configuration=None):
        """Thesaurus exporter internal write method"""
        raise NotImplementedError

    def write(self, thesaurus, output, configuration=None):
        """Thesaurus exporter write method"""
        doc = self._write(thesaurus, configuration)
        doc.write(output, encoding='utf-8', xml_declaration=True,
                  standalone=True, pretty_print=True)
        return {'Content-Type': 'text/xml; encoding=utf-8'}


@implementer(IThesaurusExporter)
class BaseThesaurusExporter:
    """Base thesaurus exporter"""

    handler = None

    def export(self, thesaurus, configuration=None):
        """Thesaurus export"""
        handler = self.handler(configuration)  # pylint: disable=not-callable
        output = TemporaryFile()
        result = handler.write(thesaurus, output, configuration)
        request = query_request()
        if request is not None:
            filename = translate_string(configuration.filename or (thesaurus.name + '.xml'),
                                        escape_slashes=True, force_lower=False, spaces='-')
            request.response.headers.extend({
                'Content-Type': result.get('Content-Type', 'text/plain'),
                'Content-Disposition': 'attachment; filename="{0}"'.format(filename)
            })
        return output


@vocabulary_config(name=THESAURUS_EXPORTERS_VOCABULARY)
class ThesaurusExportersVocabulary(UtilityVocabulary):
    """Thesaurus exporters vocabulary"""

    interface = IThesaurusExporter
    nameOnly = True
