# -*- coding: utf-8 -*-

from pip_services3_commons.convert import TypeCode
from pip_services3_commons.validate import ObjectSchema


class EntityV1Schema(ObjectSchema):
    def __init__(self):
        super().__init__()

        self.with_optional_property('id', TypeCode.String)
        self.with_required_property('site_id', TypeCode.String)
        self.with_optional_property('type', TypeCode.String)
        self.with_optional_property('name', TypeCode.String)
        self.with_optional_property('content', TypeCode.String)
