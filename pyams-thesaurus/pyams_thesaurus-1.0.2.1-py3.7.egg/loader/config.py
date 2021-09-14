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

"""PyAMS_thesaurus.loader.config module

"""

__docformat__ = 'restructuredtext'

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_thesaurus.interfaces.loader import IThesaurusExporterConfiguration, \
    IThesaurusLoaderConfiguration, IThesaurusUpdaterConfiguration
from pyams_utils.factory import factory_config


@implementer(IThesaurusLoaderConfiguration)
class ThesaurusLoaderConfiguration:
    """Thesaurus loader configuration"""

    name = FieldProperty(IThesaurusLoaderConfiguration['name'])
    data = FieldProperty(IThesaurusLoaderConfiguration['data'])
    format = FieldProperty(IThesaurusLoaderConfiguration['format'])
    import_synonyms = FieldProperty(IThesaurusLoaderConfiguration['import_synonyms'])
    language = FieldProperty(IThesaurusLoaderConfiguration['language'])
    encoding = FieldProperty(IThesaurusLoaderConfiguration['encoding'])

    def __init__(self, data=None):
        if data:
            name = data.get('name')
            if name:
                self.name = name
            self.data = data.get('data')
            self.format = data.get('format')
            self.import_synonyms = data.get('import_synonyms')
            self.language = data.get('language')
            self.encoding = data.get('encoding')


@factory_config(IThesaurusUpdaterConfiguration)
class ThesaurusUpdaterConfiguration(ThesaurusLoaderConfiguration):
    """Thesaurus updater configuration"""

    clear = FieldProperty(IThesaurusUpdaterConfiguration['clear'])
    conflict_suffix = FieldProperty(IThesaurusUpdaterConfiguration['conflict_suffix'])

    def __init__(self, data=None):
        super().__init__(data)
        if data:
            self.clear = data.get('clear')
            self.conflict_suffix = data.get('conflict_suffix')


@factory_config(IThesaurusExporterConfiguration)
class ThesaurusExporterConfiguration:
    """Thesaurus exporter configuration"""

    filename = FieldProperty(IThesaurusExporterConfiguration['filename'])
    format = FieldProperty(IThesaurusExporterConfiguration['format'])
    extract = FieldProperty(IThesaurusExporterConfiguration['extract'])

    def __init__(self, data=None):
        if data:
            self.filename = data.get('filename')
            self.format = data.get('format')
            self.extract = data.get('extract')
