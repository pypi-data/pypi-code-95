#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/5 19:53
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: parameter.py
# @Software: PyCharm
"""
import typing

from marshmallow import Schema, fields, post_load
from smart7_orm.models import Model

from starlette_utils.exception.exceptions import ValidationError

CONVERTOR_TYPES = {
    'StringConvertor': {'type': 'string'},
    'PathConvertor': {'type': 'string', 'format': 'url'},
    'IntegerConvertor': {'type': 'integer'},
    'FloatConvertor': {'type': 'number'},
    'UUIDConvertor': {'type': 'string', 'format': 'uuid'},
}


class ResponseSchema(Schema):
    code = fields.Int()
    data = fields.Dict()
    isSuccess = fields.Boolean()
    message = fields.String()


class BaseSchema(Schema):
    def __init__(self, data: dict = None, instance: [Model, typing.List[Model]] = None, many: bool = False, *args,
                 **kwargs):
        self._instance = instance
        super().__init__(context=data, many=many, *args, **kwargs)

    @property
    def data(self):
        if self._instance:
            return self.dump(self.instance, many=self.many)
        return self.context

    @property
    def valid_data(self):
        errors = self.validate(data=self.context, many=self.many, partial=self.partial)
        if errors:
            raise ValidationError(data=errors)
        return self.data

    @property
    def instance(self) -> (Model, typing.List[Model]):
        if self._instance:
            return self._instance
        if self.context:
            return self.load(self.context, many=self.many, partial=self.partial)
        return None

    @post_load
    def make_obj(self, data: dict, many, **kwargs) -> (Model, typing.List[Model]):
        if self.Meta.model:
            if many:
                obj_list = []
                for _dict in data:
                    obj_list.append(self.Meta.model(**_dict))
                return obj_list
            return self.Meta.model(**data)
        else:
            return None

    class Meta:
        model = None
