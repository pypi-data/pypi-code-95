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

from marshmallow import Schema, fields, post_load, missing
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


PRE_DUMP = "pre_dump"
POST_DUMP = "post_dump"
_T = typing.TypeVar("_T")


class AsyncDump:
    """
    异步序列化
    """

    async def async_dump(self, obj, many):
        many = self.many if many is None else bool(many)
        if self._has_processors(PRE_DUMP):
            processed_obj = self._invoke_dump_processors(
                PRE_DUMP, obj, many=many, original_data=obj
            )
        else:
            processed_obj = obj

        result = await self._async_serialize(processed_obj, many=many)

        if self._has_processors(POST_DUMP):
            result = self._invoke_dump_processors(
                POST_DUMP, result, many=many, original_data=obj
            )

        return result

    async def _async_serialize(
            self, obj: typing.Union[_T, typing.Iterable[_T]], *, many: bool = False
    ):
        """Serialize ``obj``.

        :param obj: The object(s) to serialize.
        :param bool many: `True` if ``data`` should be serialized as a collection.
        :return: A dictionary of the serialized data

        .. versionchanged:: 1.0.0
            Renamed from ``marshal``.
        """
        if many and obj is not None:
            return [
                await self._async_serialize(d, many=False)
                for d in typing.cast(typing.Iterable[_T], obj)
            ]
        ret = self.dict_class()
        for attr_name, field_obj in self.dump_fields.items():
            value = field_obj.serialize(attr_name, obj, accessor=self.get_attribute)
            if hasattr(value, '__await__'):
                value = await field_obj.serialize(attr_name, obj, accessor=self.get_attribute)
            if value is missing:
                continue
            key = field_obj.data_key if field_obj.data_key is not None else attr_name
            ret[key] = value
        return ret


class BaseSchema(Schema, AsyncDump):
    def __init__(self, data: dict = None, instance: [Model, typing.List[Model]] = None, many: bool = False, *args,
                 **kwargs):
        self._instance = instance
        super().__init__(context=data, many=many, *args, **kwargs)

    @property
    async def data(self):
        if self._instance:
            return await self.async_dump(self.instance, many=self.many)
        return self.context

    @property
    def sync_data(self):
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
