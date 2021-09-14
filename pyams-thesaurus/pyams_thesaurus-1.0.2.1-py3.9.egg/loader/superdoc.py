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

"""PyAMS_thesaurus.loader.superdoc module

This module is used to import or export thesaurus in Superdoc format.
"""

from datetime import datetime

import chardet
from lxml import etree
from zope.intid import IIntIds

from pyams_thesaurus.interfaces.loader import IThesaurusExporter, IThesaurusLoader
from pyams_thesaurus.loader import BaseThesaurusExporter, BaseThesaurusLoader, \
    ThesaurusLoaderDescription, ThesaurusLoaderTerm, XMLThesaurusExporterHandler, \
    XMLThesaurusLoaderHandler
from pyams_utils.registry import get_utility, utility_config


__docformat__ = 'restructuredtext'


# namespaces definitions

INM = "{http://www.inmagic.com/webpublisher/query}"


class SuperdocThesaurusLoaderHandler(XMLThesaurusLoaderHandler):
    """SuperDoc format thesaurus load handler"""

    def read(self, data, configuration=None):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks
        """Thesaurus file read"""
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
        # get thesaurus description
        description = ThesaurusLoaderDescription()
        if configuration:
            description.language = configuration.language
        # check thesaurus terms
        for records in root.findall(INM + 'Recordset'):  # pylint: disable=too-many-nested-blocks
            for record in records.findall(INM + 'Record'):
                key = None
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
                for element in record.getchildren():
                    if element.text:
                        if element.tag == INM + 'Terme':
                            key = label = str(element.text)
                        elif element.tag == INM + 'NA':
                            definition = str(element.text)
                        elif element.tag == INM + 'TS':
                            specifics.append(str(element.text))
                        elif element.tag == INM + 'TG':
                            generic = str(element.text)
                        elif element.tag == INM + 'TA':
                            associations.append(str(element.text))
                        elif element.tag == INM + 'EM':
                            if configuration and configuration.import_synonyms:
                                usage = str(element.text)
                        elif element.tag == INM + 'EP':
                            if configuration and configuration.import_synonyms:
                                used_for.append(str(element.text))
                        elif element.tag == INM + 'Notes':
                            note = str(element.text)
                        elif element.tag == INM + 'DateCreation':
                            created = datetime.strptime(element.text, '%d/%m/%Y')
                        elif element.tag == INM + 'DateModification':
                            modified = datetime.strptime(element.text, '%d/%m/%Y')
                if key:
                    terms[key] = ThesaurusLoaderTerm(label, alt, definition, note,
                                                     generic, specifics, associations,
                                                     usage, used_for, created, modified)
        return description, terms


@utility_config(name='SuperDoc',
                provides=IThesaurusLoader)
class SuperdocThesaurusLoader(BaseThesaurusLoader):
    """SuperDoc export format thesaurus loader"""

    handler = SuperdocThesaurusLoaderHandler


class SuperdocThesaurusExporterHandler(XMLThesaurusExporterHandler):
    """SuperDoc format thesaurus export handler"""

    def _write(self, thesaurus, configuration=None):  # pylint: disable=too-many-branches,too-many-statements
        intids = get_utility(IIntIds)
        xml = etree.Element('Results', nsmap={None: INM[1:-1]},
                            productTitle='PyAMS Thesaurus Manager',
                            productVersion='1.0')
        doc = etree.ElementTree(xml)
        extract = configuration.extract if configuration else None
        if extract:
            terms = [
                term for term in thesaurus.terms.values()
                if extract in (term.extracts or set())
            ]
        else:
            terms = thesaurus.terms
        rs = etree.SubElement(xml, 'Recordset', setCount=str(len(terms)))  # pylint: disable=invalid-name
        for index, term in enumerate(thesaurus.terms.values()):
            if extract and (extract not in (term.extracts or set())):
                continue
            rec = etree.SubElement(rs, 'Record', setEntry=str(index))
            etree.SubElement(rec, 'ID').text = str(intids.queryId(term))
            etree.SubElement(rec, 'Terme').text = term.label
            etree.SubElement(rec, 'NA').text = term.note
            added_subterms = False
            if term.specifics:
                for subterm in term.specifics:
                    if extract and (extract not in (subterm.extracts or ())):
                        continue
                    etree.SubElement(rec, 'TS').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, 'TS')
            sub = etree.SubElement(rec, 'TG')
            if term.generic:
                sub.text = term.generic.label
            added_subterms = False
            if term.associations:
                for subterm in term.associations:
                    if extract and (extract not in (subterm.extracts or ())):
                        continue
                    etree.SubElement(rec, 'TA').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, 'TA')
            sub = etree.SubElement(rec, 'EM')
            if term.usage:
                sub.text = term.usage.label
            added_subterms = False
            if term.used_for:
                for subterm in term.used_for:
                    if extract and (extract not in (subterm.extracts or ())):
                        continue
                    etree.SubElement(rec, 'EP').text = subterm.label
                    added_subterms = True
            if not added_subterms:
                etree.SubElement(rec, 'EP')
            etree.SubElement(rec, 'Notes').text = term.definition
            etree.SubElement(rec, 'Status').text = term.status
            etree.SubElement(rec, 'DateCreation').text = term.created.strftime('%d/%m/%Y') \
                if term.created else ''
            etree.SubElement(rec, 'DateModification').text = term.modified.strftime('%d/%m/%Y') \
                if term.modified else ''
            etree.SubElement(rec, 'Niveau').text = str(term.level)
            etree.SubElement(rec, 'MicroThes').text = 'oui' if term.micro_thesaurus else 'NON'
            etree.SubElement(rec, 'Terme0').text = term.label \
                if term.parent is None else term.parent.label
        return doc


@utility_config(name='SuperDoc',
                provides=IThesaurusExporter)
class SuperdocThesaurusExporter(BaseThesaurusExporter):
    """SuperDoc format thesaurus exporter"""

    handler = SuperdocThesaurusExporterHandler
