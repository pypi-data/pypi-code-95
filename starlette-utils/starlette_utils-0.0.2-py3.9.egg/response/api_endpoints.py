#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/7/20 9:59 下午
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: api_endpoints.py
# @Software: PyCharm
"""

from starlette.requests import Request

from .base_endpoints import BaseApiViews
from .responseViewMixin import ResponseViewMixin


class ListApiView(ResponseViewMixin, BaseApiViews):
    async def get(self, request: Request, *args, **kwargs):
        return await self.handler(request, *args, **kwargs)

    async def handler(self, request: Request, *args, **kwargs):
        self.valid_serializer_class()
        instances = await self.filter_queryset(self.get_queryset())
        return self.success(self.serializer_class(many=True).dump(instances))


class RetrieveApiView(ResponseViewMixin, BaseApiViews):
    pk_field = 'id'

    async def get(self, request: Request, *args, **kwargs):
        return await self.handler(request, *args, **kwargs)

    async def handler(self, request: Request, *args, **kwargs):
        self.valid_serializer_class()
        instance = await self.get_object()
        return self.success(self.serializer_class().dump(instance))


class CreateApiView(ResponseViewMixin, BaseApiViews):
    async def post(self, request: Request, *args, **kwargs):
        return await self.handler(request, *args, **kwargs)

    async def handler(self, request: Request, *args, **kwargs):
        self.valid_serializer_class()
        serializers = self.serializer_class(self.data)
        instance = serializers.instance
        await instance.save()
        return self.success(self.serializer_class(instance=instance).data)


class UpdateApiView(ResponseViewMixin, BaseApiViews):
    pk_field = 'id'

    async def patch(self, request: Request, *args, **kwargs):
        kwargs['is_patch'] = True
        return await self.put(request, *args, **kwargs)

    async def put(self, request: Request, *args, **kwargs):
        return await self.handler(request, *args, **kwargs)

    async def handler(self, request: Request, *args, **kwargs):
        self.valid_serializer_class()
        is_patch = kwargs.get('is_patch', False)
        partial = self.get_partial() if is_patch else False
        serializers = self.serializer_class(data=self.data, partial=partial)
        instance = await self.get_object()
        instance = instance.update_from_dict(serializers.valid_data)
        await instance.save()
        return self.success(self.serializer_class(instance=instance).data)

    def get_partial(self):
        partial = tuple(set(self.serializer_class._declared_fields.keys()).difference(set(self.data.keys())))
        return partial


class DeleteApiView(ResponseViewMixin, BaseApiViews):
    pk_field = 'id'

    async def delete(self, request: Request, *args, **kwargs):
        return await self.handler(request, *args, **kwargs)

    async def handler(self, request: Request, *args, **kwargs):
        instance = await self.get_object()
        await instance.delete()
        return self.success('ok')
