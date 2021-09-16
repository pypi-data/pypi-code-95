# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.middlewares.route_coverage.coverage_utils import (
    CoverageUtils,
    DEFAULT_ROUTE_METHODS,
)

DEFAULT_ROUTE_METHODS = DEFAULT_ROUTE_METHODS + ("HEAD",)


def create_fastapi_routes(app):
    """
    Returns all the routes registered to a FastAPI app as a dict
    :param app: FastAPI app instance
    :return: dict {route_id:  RouteCoverage}
    """
    routes = {}

    for app_route in app.routes:
        view_func = app_route.endpoint
        route = build_fastapi_route(app_route.name, view_func)
        route_id = str(id(view_func))
        methods = app_route.methods or DEFAULT_ROUTE_METHODS

        for method_type in methods:
            key = CoverageUtils.build_key(route_id, method_type)
            routes[key] = CoverageUtils.build_route_coverage(
                verb=method_type,
                url=CoverageUtils.get_normalized_uri(str(app_route.name)),
                route=route,
            )

    return routes


def build_fastapi_route(view_func_name, view_func):
    view_func_args = CoverageUtils.build_args_from_function(view_func)
    return view_func_name + view_func_args
