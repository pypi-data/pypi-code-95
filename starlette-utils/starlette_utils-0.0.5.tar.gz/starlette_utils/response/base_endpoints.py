#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/7/25 9:36 上午
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: base_endpoints.py
# @Software: PyCharm
"""
import abc
import typing
from json import JSONDecodeError

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.types import Scope, Receive, Send
from tortoise import Model
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from starlette_utils.exception.exceptions import ApiException, NotFondException, MultipleFondException
from starlette_utils.schemas.schema import BaseSchema


class BaseApiViews(HTTPEndpoint):
    model_class: typing.Type[Model] = None
    serializer_class: typing.Type[BaseSchema] = None
    filter_class: typing.Type[BaseSchema] = None
    pk_field = None
    look_up_field = None
    filter_params = []

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.request = None
        self.queryset = None
        self.data = None
        self.kwargs = dict()
        self.query_params = dict()
        super().__init__(scope, receive, send)

    async def dispatch(self) -> None:
        self.request = Request(self.scope, receive=self.receive)
        try:
            self.data = await self.request.json()
        except JSONDecodeError:
            self.data = {}
        self.kwargs = self.request.path_params
        self.query_params = self.request.query_params
        try:
            await super().dispatch()
        except Exception as e:
            if isinstance(e, ApiException):
                raise e
            # raise ApiException(detail=e.__str__())
            raise e

    @abc.abstractmethod
    async def handler(self, request: Request, *args, **kwargs):
        """
        视图处理方法

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def get_queryset(self):
        """
        获取查询集

        :return:
        """
        assert self.model_class is not None, (
            "model_class is required or override the `get_queryset()` method."
        )

        self.queryset = self.model_class.all()
        return self.queryset

    def filter_queryset(self, queryset):
        """
        获取筛选集合

        :param queryset:
        :return:
        """
        filter_args = dict()
        for filter_param in self.filter_params:
            filter_args[filter_param] = self.query_params.get(filter_param)
        return queryset.filter(**filter_args)

    async def get_object(self) -> Model:
        """
        获取模型对象实例

        :return:
        """
        assert self.model_class is not None, (
            "model_class is required or override the `get_object()` method."
        )
        assert self.pk_field or self.look_up_field, (
            'pk_field or look_up_field is required'
        )
        look_up_field = self.pk_field or self.look_up_field
        object_look_up = self.kwargs[look_up_field]
        try:
            instance = await (self.filter_queryset(self.get_queryset())).get(**{
                look_up_field: object_look_up
            })
        except DoesNotExist:
            raise NotFondException()
        except MultipleObjectsReturned:
            raise MultipleFondException()
        return instance

    def valid_serializer_class(self):
        """
        校验序列化器是否设置
        """
        if not self.serializer_class:
            raise ApiException('serializer_class is not defined')
