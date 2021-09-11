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

"""PyAMS_utils.rest module

This module provides OpenAPI documentation for all provided
Cornice REST endpoints.
"""

from cgi import FieldStorage

from colander import Date, Mapping, SchemaNode, SequenceSchema, String, Tuple, TupleSchema, drop, \
    null
from cornice import Service
from cornice.service import get_services
from cornice_swagger import CorniceSwagger
from cornice_swagger.converters.schema import ArrayTypeConverter, ObjectTypeConverter, \
    StringTypeConverter


__docformat__ = 'restructuredtext'

from pyams_utils import _


class StringListSchema(SequenceSchema):
    """Strings list list"""
    value = SchemaNode(String(),
                       title=_("Item value"),
                       missing=drop)


class StringListTypeConverter(ArrayTypeConverter):
    """Strings list type converter"""


class PropertiesMapping(Mapping):
    """Properties schema"""

    name = 'properties'

    def serialize(self, node, appstruct):
        if appstruct is null:
            return {}
        return appstruct

    def deserialize(self, node, cstruct):
        return cstruct


class PropertiesMappingTypeConverter(ObjectTypeConverter):
    """Properties mapping type converter"""


class DateRangeSchema(TupleSchema):
    """Dates range schema type"""
    after = SchemaNode(Date(),
                       title=_("Range beginning date"),
                       missing=null)
    before = SchemaNode(Date(),
                        title=_("Range ending date (excluded)"),
                        missing=null)


class DateRangeTypeConverter(ArrayTypeConverter):
    """Date range type converter"""


class FileUploadType(String):
    """File upload type"""

    def serialize(self, node, appstruct):
        """File upload serializer"""
        return super().serialize(node, appstruct)

    def deserialize(self, node, cstruct):
        """File upload deserializer"""
        if isinstance(cstruct, FieldStorage):
            return cstruct
        return super().deserialize(node, cstruct)


class FileUploadTypeConverter(StringTypeConverter):
    """File upload type converter"""


# update Cornice-Swagger types converters
CorniceSwagger.custom_type_converters.update({
    Tuple: ArrayTypeConverter,
    StringListSchema: StringListTypeConverter,
    PropertiesMapping: PropertiesMappingTypeConverter,
    DateRangeSchema: DateRangeTypeConverter,
    FileUploadType: FileUploadTypeConverter
})


swagger = Service(name='OpenAPI',
                  path='/__api__',
                  description="OpenAPI documentation")


@swagger.get()
def openapi_specification(request):  # pylint: disable=unused-argument
    """OpenAPI specification"""
    doc = CorniceSwagger(get_services())
    doc.summary_docstrings = True
    return doc.generate('PyAMS', '1.0')
