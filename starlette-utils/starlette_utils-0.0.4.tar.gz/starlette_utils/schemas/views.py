#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/5 19:39
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: views.py
# @Software: PyCharm
"""
from starlette.responses import JSONResponse

from .schemas import schemas
from starlette_utils.response import api_endpoints


class OpenApi(api_endpoints.RetrieveApiView):
    routes = []

    @classmethod
    def get_schemas(cls, routes):
        cls.routes = routes
        return OpenApi

    def get(self, request, *args, **kwargs):
        return JSONResponse(schemas.get_schema(self.routes))
