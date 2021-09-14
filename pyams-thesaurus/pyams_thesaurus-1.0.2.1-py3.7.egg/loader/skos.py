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

"""PyAMS_thesaurus.loader.skos module

This module is used to import or export thesaurus in SKOS/RDF format.
"""

import chardet
from lxml import etree

from pyams_thesaurus.interfaces.loader import IThesaurusExporter, IThesaurusLoader
from pyams_thesaurus.loader import BaseThesaurusExporter, BaseThesaurusLoader, \
    ThesaurusLoaderDescription, ThesaurusLoaderTerm, XMLThesaurusExporterHandler, \
    XMLThesaurusLoaderHandler
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


# XML namespaces

XML = '{http://www.w3.org/XML/1998/namespace}'
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
RDFS = '{http://www.w3.org/2000/01/rdf-schema#}'
DC = '{http://purl.org/dc/elements/1.1/}'
DCT = '{http://purl.org/dc/terms/}'
MAP = '{http://www.w3c.rl.ac.uk/2003/11/21-skos-mapping#}'
SKOS = '{http://www.w3.org/2004/02/skos/core#}'


class SKOSThesaurusLoaderHandler(XMLThesaurusLoaderHandler):
    """SKOS format thesaurus handler"""

    def read(self, data, configuration=None):  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        """Thesaurus loader reader"""
        terms = {}
        if configuration is None:
            configuration = self.configuration
        encoding = None
        if configuration and configuration.encoding:
            encoding = configuration.encoding
        if (not encoding) and isinstance(data, str):
            encoding = chardet.detect(data[:1000]).get('encoding', 'utf-8')
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding=encoding)
        xml = etree.parse(data, parser=parser)
        root = xml.getroot()
        # check thesaurus scheme
        description = ThesaurusLoaderDescription()
        scheme = root.find('.//' + SKOS + 'ConceptScheme')
        if scheme is not None:
            for element in scheme.getchildren():
                if element.tag == DC + 'title':
                    description.title = str(element.text)
                elif element.tag == DC + 'creator':
                    description.creator = str(element.text)
                elif element.tag == DC + 'subject':
                    description.subject = str(element.text)
                elif element.tag == DC + 'description':
                    description.description = str(element.text)
                elif element.tag == DC + 'publisher':
                    description.publisher = str(element.text)
                elif element.tag == DC + 'date':
                    description.created = str(element.text)
                elif element.tag == DC + 'language':
                    description.language = element.text
        if configuration and not description.language:
            description.language = configuration.language
        # check thesaurus terms
        for concept in root.findall(SKOS + 'Concept'):
            key = concept.attrib.get(RDF + 'about')
            label = None
            alt = None
            definition = None
            note = None
            generic = None
            specifics = []
            associations = []
            usage = None
            used_for = []
            created = None
            modified = None
            for element in concept.getchildren():
                if element.tag == SKOS + 'prefLabel':
                    label = str(element.text)
                elif element.tag == SKOS + 'altLabel':
                    term = element.attrib.get(RDF + 'resource')
                    if term is not None:
                        # import synonyms ?
                        if not configuration.import_synonyms:
                            continue
                        # link to another synonym resource
                        used_for.append(term)
                        if term not in terms:
                            # initialize synonym with usage field
                            terms[term] = ThesaurusLoaderTerm(term, alt='', definition='',
                                                              note='', generic='',
                                                              specifics='', associations='',
                                                              usage=key, used_for=[])
                        else:
                            terms[term].usage = key
                    else:
                        # just an alternate label
                        alt = str(element.text)
                elif element.tag == SKOS + 'definition':
                    definition = str(element.text)
                elif element.tag in (SKOS + 'note', SKOS + 'scopeNote'):
                    note = str(element.text)
                elif element.tag == SKOS + 'related':
                    associations.append(str(element.attrib[RDF + 'resource']))
                elif element.tag == SKOS + 'broader':
                    generic = str(element.attrib[RDF + 'resource'])
                elif element.tag == SKOS + 'narrower':
                    specifics.append(str(element.attrib[RDF + 'resource']))
                elif element.tag == DCT + 'created':
                    created = element.text
            if key not in terms:
                terms[key] = ThesaurusLoaderTerm(label, alt, definition, note,
                                                 generic, specifics, associations,
                                                 usage, used_for, created, modified)
            else:
                # update an already initialized synonym
                term = terms[key]
                term.label = label
                term.alt = alt
                term.definition = definition
                term.note = note
                term.generic = generic
                term.specifics = specifics
                term.associations = associations
                term.usage = usage
                term.used_for = used_for
                term.created = created
                term.modified = modified
        return description, terms


@utility_config(name='SKOS (RDF)',
                provides=IThesaurusLoader)
class SKOSThesaurusLoader(BaseThesaurusLoader):
    """SKOS format thesaurus loader"""

    handler = SKOSThesaurusLoaderHandler


class SKOSThesaurusExporterHandler(XMLThesaurusExporterHandler):
    """SKOS/RDF format thesaurus export handler"""

    def _write(self, thesaurus, configuration=None):  # pylint: disable=too-many-branches
        thesaurus_url = 'Thesaurus/{}'.format(thesaurus.__name__)
        nsmap = {
            'rdf': RDF[1:-1],
            'rdfs': RDFS[1:-1],
            'dc': DC[1:-1],
            'dct': DCT[1:-1],
            'map': MAP[1:-1],
            'skos': SKOS[1:-1]
        }
        xml = etree.Element(RDF + 'RDF', nsmap=nsmap)
        doc = etree.ElementTree(xml)
        cs = etree.SubElement(xml, SKOS + 'ConceptScheme')  # pylint: disable=invalid-name
        cs.attrib[RDF + 'about'] = thesaurus_url
        etree.SubElement(cs, DC + 'title').text = thesaurus.title
        etree.SubElement(cs, DC + 'creator').text = thesaurus.creator
        etree.SubElement(cs, DC + 'subject').text = thesaurus.subject
        if thesaurus.description:
            etree.SubElement(cs, DC + 'description').text = etree.CDATA(thesaurus.description)
        etree.SubElement(cs, DC + 'publisher').text = thesaurus.publisher
        if thesaurus.created:
            etree.SubElement(cs, DC + 'date').text = thesaurus.created.strftime('%Y-%m-%d')
        etree.SubElement(cs, DC + 'language').text = thesaurus.language
        extract = configuration.extract if configuration else None
        for term in thesaurus.top_terms:
            if extract and (extract not in (term.extracts or ())):
                continue
            etree.SubElement(cs, SKOS + 'hasTopConcept').attrib[RDF + 'resource'] = \
                term.short_url()
        for term in thesaurus.terms.values():
            if extract and (extract not in (term.extracts or ())):
                continue
            concept = etree.SubElement(xml, SKOS + 'Concept')
            concept.attrib[RDF + 'about'] = term.short_url()
            sub = etree.SubElement(concept, SKOS + 'prefLabel')
            sub.attrib[XML + 'lang'] = thesaurus.language
            sub.text = term.label
            etree.SubElement(concept, SKOS + 'inScheme').attrib[RDF + 'resource'] = thesaurus_url
            if term.definition:
                sub = etree.SubElement(concept, SKOS + 'definition')
                sub.attrib[XML + 'lang'] = thesaurus.language
                sub.text = term.definition
            if term.note:
                sub = etree.SubElement(concept, SKOS + 'scopeNote')
                sub.attrib[XML + 'lang'] = thesaurus.language
                sub.text = etree.CDATA(term.note)
            for subterm in term.associations:
                if extract and (extract not in (subterm.extracts or ())):
                    continue
                etree.SubElement(concept, SKOS + 'related').attrib[RDF + 'resource'] = \
                    subterm.short_url()
            if term.generic:
                etree.SubElement(concept, SKOS + 'broader').attrib[RDF + 'resource'] = \
                    term.generic.short_url()
            for subterm in term.used_for:
                if extract and (extract not in (subterm.extracts or ())):
                    continue
                etree.SubElement(concept, SKOS + 'altLabel').attrib[RDF + 'resource'] = \
                    subterm.short_url()
            for subterm in term.specifics:
                if extract and (extract not in (subterm.extracts or ())):
                    continue
                etree.SubElement(concept, SKOS + 'narrower').attrib[RDF + 'resource'] = \
                    subterm.short_url()
            if term.created:
                etree.SubElement(concept, DCT + 'created').text = \
                    term.created.strftime('%Y-%m-%d %H:%M:%S')
        return doc


@utility_config(name='SKOS (RDF)',
                provides=IThesaurusExporter)
class SKOSThesaurusExporter(BaseThesaurusExporter):
    """SKOS/RDF format thesaurus exporter"""

    handler = SKOSThesaurusExporterHandler
