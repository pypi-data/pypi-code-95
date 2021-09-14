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

"""PyAMS_thesaurus.interfaces.loader module

This module defines interfaces of utilities used to import or export
thesaurus contents into several formats.
"""

from zope.interface import Attribute, Interface
from zope.schema import Bool, Choice, TextLine

from pyams_file.schema import FileField
from pyams_i18n.interfaces import BASE_LANGUAGES_VOCABULARY_NAME
from pyams_thesaurus.interfaces import THESAURUS_EXTRACTS_VOCABULARY
from pyams_thesaurus.schema import ValidatedChoice
from pyams_utils.schema import EncodingField


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _  # pylint: disable=ungrouped-imports


THESAURUS_LOADERS_VOCABULARY = 'pyams_thesaurus.loaders'


class IThesaurusLoaderConfiguration(Interface):
    """Thesaurus loader configuration interface"""

    name = TextLine(title=_("Thesaurus name"),
                    description=_("Name of the registered thesaurus"),
                    required=True)

    data = FileField(title=_("Input data"),
                     description=_("Input file containing thesaurus data"),
                     required=True)

    format = Choice(title=_("File format"),
                    description=_("This list contains available thesauri loaders"),
                    required=True,
                    vocabulary=THESAURUS_LOADERS_VOCABULARY)

    import_synonyms = Bool(title=_("Import synonyms?"),
                           description=_("If 'No', synonyms will not be imported into loaded "
                                         "thesaurus"),
                           required=True,
                           default=True)

    language = Choice(title=_("Content language"),
                      description=_("Select file language, for formats which don't provide "
                                    "it internally"),
                      required=False,
                      vocabulary=BASE_LANGUAGES_VOCABULARY_NAME)

    encoding = EncodingField(title=_("File encoding"),
                             description=_("Select file encoding, for formats which don't "
                                           "provide it internally"),
                             required=False,
                             default='utf-8')


class IThesaurusUpdaterConfiguration(IThesaurusLoaderConfiguration):
    """Thesaurus updater configuration interface"""

    clear = Bool(title=_("Clear before merge ?"),
                 description=_("If 'yes', thesaurus will be cleared before re-importing file "
                               "contents"),
                 required=True,
                 default=False)

    conflict_suffix = TextLine(title=_("Auto-added conflict suffix"),
                               description=_("If you want to prevent imports conflicts, you "
                                             "can provide a suffix which will be added "
                                             "automatically to conflicting terms"),
                               required=False)


class IThesaurusLoaderHandler(Interface):
    """Thesaurus loader handler configuration"""

    configuration = Attribute("Current handler configuration")

    def read(self, data, configuration=None):
        """Extract terms from given data"""


class IThesaurusLoader(Interface):
    """Thesaurus loader interface"""

    handler = Attribute("Thesaurus handler class")

    def load(self, data, configuration=None):
        """Load thesaurus from data for the given loader configuration"""


THESAURUS_EXPORTERS_VOCABULARY = 'pyams_thesaurus.exporters'


class IThesaurusExporterConfiguration(Interface):
    """Thesaurus exporter configuration interface"""

    filename = TextLine(title=_("Export file name"),
                        description=_("Full file name, including extension"),
                        required=False)

    format = Choice(title=_("Export file format"),
                    description=_("This list contains available thesauri exporters"),
                    required=True,
                    vocabulary=THESAURUS_EXPORTERS_VOCABULARY)

    extract = ValidatedChoice(title=_("Extract to export"),
                              description=_("You can choose to export only an extract of the "
                                            "thesaurus"),
                              required=False,
                              vocabulary=THESAURUS_EXTRACTS_VOCABULARY)


class IThesaurusExporterHandler(Interface):
    """Thesaurus exporter handler configuration"""

    content_type = Attribute("Content type of export file")

    configuration = Attribute("Current handler configuration")

    def write(self, thesaurus, output, configuration=None):
        """Export terms of given thesaurus"""


class IThesaurusExporter(Interface):
    """Thesaurus exporter configuration"""

    handler = Attribute("Thesaurus handler class")

    def export(self, thesaurus, configuration=None):
        """Export thesaurus terms with the given export configuration"""
