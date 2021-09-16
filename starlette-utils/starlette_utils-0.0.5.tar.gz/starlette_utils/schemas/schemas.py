#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/5 19:38
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: schemas.py
# @Software: PyCharm
"""
import inspect
import typing

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from starlette.routing import BaseRoute, Mount, Route
from starlette_apispec.schemas import make_plain_datastructure, APISpecSchemaGenerator

from .schema import ResponseSchema, CONVERTOR_TYPES, BaseSchema
from . import schema_settings as settings


class EndpointInfo(typing.NamedTuple):
    path: str
    http_method: str
    func: typing.Callable
    param_convertors: dict = {}
    docstring: str = ''
    schema: typing.Type[BaseSchema] = None
    params: typing.Type[BaseSchema] = None


class SchemaGenerator(APISpecSchemaGenerator):
    def get_schema(self, routes: typing.List[BaseRoute]) -> dict:
        raise NotImplementedError()  # pragma: no cover

    def get_endpoints(
            self, routes: typing.List[BaseRoute]
    ) -> typing.List[EndpointInfo]:
        """
        Given the routes, yields the following information:

        - path
            eg: /users/
        - http_method
            one of 'get', 'post', 'put', 'patch', 'delete', 'options'
        - func
            method ready to extract the docstring
        """
        endpoints_info: list = []

        for route in routes:
            if isinstance(route, Mount):
                routes = route.routes or []
                sub_endpoints = [
                    EndpointInfo(
                        path="".join((route.path, sub_endpoint.path)),
                        http_method=sub_endpoint.http_method,
                        func=sub_endpoint.func,
                        param_convertors=sub_endpoint.param_convertors,
                        docstring=sub_endpoint.docstring,
                        schema=sub_endpoint.schema,
                        params=sub_endpoint.params,
                    )
                    for sub_endpoint in self.get_endpoints(routes)
                ]
                endpoints_info.extend(sub_endpoints)

            elif not isinstance(route, Route) or not route.include_in_schema:
                continue

            elif inspect.isfunction(route.endpoint) or inspect.ismethod(route.endpoint):
                for method in route.methods or ["GET"]:
                    if method == "HEAD":
                        continue
                    endpoints_info.append(
                        EndpointInfo(
                            route.path_format,
                            method.lower(),
                            route.endpoint,
                            route.param_convertors,
                            docstring=route.endpoint.__doc__ or route.endpoint.__name__,
                            schema=route.endpoint.serializer_class,
                            params=route.endpoint.filter_class,
                        )
                    )
            else:
                for method in ["get", "post", "put", "patch", "delete", "options"]:
                    if not hasattr(route.endpoint, method):
                        continue
                    func = getattr(route.endpoint, method)
                    endpoints_info.append(
                        EndpointInfo(
                            route.path_format,
                            method.lower(),
                            func,
                            route.param_convertors,
                            docstring=route.endpoint.__doc__ or route.endpoint.__name__,
                            schema=route.endpoint.serializer_class,
                            params=route.endpoint.filter_class,
                        )
                    )

        return endpoints_info

    def get_schema(self, routes: typing.List[BaseRoute]) -> dict:
        endpoints: typing.List[EndpointInfo] = self.get_endpoints(routes)
        for endpoint in endpoints:
            self.spec.path(
                path=endpoint.path,
                operations={endpoint.http_method: self.parse_docstring(
                    endpoint, has_requestBody=endpoint.http_method in ['post', 'put', 'patch', ])},
            )
        return make_plain_datastructure(self.spec.to_dict())

    def parse_docstring(self, endpoint: EndpointInfo, has_requestBody: bool = False) -> dict:
        parameters = []
        docstring = endpoint.docstring.strip().split('\n')
        tags_list = [_ for _ in endpoint.path.split('/') if _]
        if tags_list.__len__() > 0:
            tags = [tags_list[0]]
        else:
            tags = []
        if docstring.__len__() > 1:
            summary = docstring[0]
            description = '\n'.join([_ for _ in docstring[1:] if _])
        else:
            summary = docstring[0]
            description = docstring[0]
        if endpoint.param_convertors:
            for param_convertor_key, param_convertor_value in endpoint.param_convertors.items():
                parameter = CONVERTOR_TYPES.get(str(param_convertor_value.__class__.__name__))
                if parameter:
                    parameters.append({
                        'in': 'path',
                        'name': param_convertor_key,
                        'required': True,
                        'schema': parameter,
                    })
        if endpoint.params:
            parameters.append({
                'in': 'query',
                'schema': endpoint.params,
            })
        responses = {
            '200': {
                'content': {'application/json': {'schema': 'ResponseSchema'}}
            }
        }
        docstring_dict = {
            'parameters': parameters,
            'description': description,
            'summary': summary,
            'responses': responses,
            'tags': tags,
        }
        # 加载提交模型schema
        if endpoint.schema and has_requestBody:
            docstring_dict.update({'requestBody': {
                'content': {'application/json': {'schema': endpoint.schema}}
            }})
        return docstring_dict


schemas = SchemaGenerator(
    spec=APISpec(**settings.SCHEMA_CONFIG)
)

schemas.spec.components.schema("Response", schema=ResponseSchema)
