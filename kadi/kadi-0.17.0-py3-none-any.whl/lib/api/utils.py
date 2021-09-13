# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import math
import re
from collections import OrderedDict
from functools import wraps

from flask import current_app
from flask import has_request_context
from flask import request

from .models import AccessToken
from kadi.ext.db import db
from kadi.lib.cache import memoize_request
from kadi.lib.db import get_class_by_tablename
from kadi.lib.utils import rgetattr
from kadi.lib.web import url_for


def status(status_code, description):
    """Decorator to add response status information to an API endpoint.

    This information is currently only used when generating the API documentation.

    :param status_code: The status code of the response.
    :param description: The description corresponding to the status code, describing
        when the status code occurs or whether there is a response body. Supports reST
        syntax.
    """

    def decorator(func):
        if hasattr(func, "_apidoc"):
            if "status_codes" in func._apidoc:
                func._apidoc["status_codes"][status_code] = description
                func._apidoc["status_codes"].move_to_end(status_code, last=False)
            else:
                func._apidoc["status_codes"] = OrderedDict([(status_code, description)])
        else:
            func._apidoc = {"status_codes": OrderedDict([(status_code, description)])}

        return func

    return decorator


def reqbody(data, description="", type="json"):
    """Decorator to add request body information to an API endpoint.

    This information is currently only used when generating the API documentation.

    :param data: The request body information as dictionary in the following form:

        .. code-block:: python3

            {
                "<field>": {
                    "type": "integer",
                    # Can be omitted, defaults to False.
                    "required": True,
                    # Flag indicating whether multiple values for the same key can be
                    # given or not. Can be omitted, defaults to False.
                    "many": False,
                }
            }

    :param description: (optional) Additional description of the request body. Supports
        reST syntax.
    :param type: (optional) The type of the request body, one of ``"json"`` or
        ``"form"``.
    """

    def decorator(func):
        apidoc_meta = {"data": data, "description": description, "type": type}

        if hasattr(func, "_apidoc"):
            func._apidoc["reqbody"] = apidoc_meta
        else:
            func._apidoc = {"reqbody": apidoc_meta}

        return func

    return decorator


def reqschema(schema, description="", bind=True):
    """Decorator to add request body information to an API endpoint using a schema.

    Similar to :func:`reqbody`, but the information about the request body is inferred
    automatically based on the given schema.

    This information is also used when generating the API documentation.

    :param schema: The schema instance to use as base for the request body information.
    :param description: (optional) Additional description of the request body. Supports
        reST syntax.
    :param bind: (optional) Flag indicating whether the schema should also be injected
        into the decorated function as keyword argument ``schema``. That way it can be
        reused more easily.
    """

    def decorator(func):
        apidoc_meta = {"schema": schema, "description": description}

        if hasattr(func, "_apidoc"):
            func._apidoc["reqschema"] = apidoc_meta
        else:
            func._apidoc = {"reqschema": apidoc_meta}

        @wraps(func)
        def decorated_view(*args, **kwargs):
            if bind:
                kwargs["schema"] = schema

            return func(*args, **kwargs)

        return decorated_view

    return decorator


def is_api_request():
    """Check if the current request is an API request.

    A request is an API request if the path of the current request path starts with
    ``"/api"``.

    :return: ``True`` if the request is an API request, ``False`` otherwise.
    """
    return (
        has_request_context() and re.match(r"^\/api($|\/.*)$", request.path) is not None
    )


def is_internal_api_request():
    """Check if the current API request is an "internal" one.

    An API request is marked as internal if it includes a query parameter ``_internal``
    with any value (e.g. ``"https://...?_internal=true"``). It does not matter whether
    the request uses the session or a personal access token.

    :return: ``True`` if the request is internal, ``False`` otherwise.
    """
    return is_api_request() and request.args.get("_internal") is not None


def get_api_version():
    """Get the API version from the current request path.

    :return: The current API version or ``None`` if the current request is not an API
        request or no valid version is found.
    """
    if is_api_request():
        api_versions = current_app.config["API_VERSIONS"]

        parts = request.path[1:].split("/")
        if len(parts) > 1 and re.match(r"^v[0-9]+\.[0-9]+$", parts[1]):
            api_version = parts[1][1:]

            if api_version in api_versions:
                return api_version

    return None


@memoize_request
def get_api_access_token():
    """Get a personal access token from the current request.

    :return: An access token object or ``None`` if no valid bearer token can be found or
        no request context currently exists.
    """
    if has_request_context():
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return AccessToken.get_by_token(parts[1])

    return None


def get_access_token_scopes():
    """Get all possible access token scopes.

    The possible scopes are currently combined from the ones set explicitly in
    ``API_SCOPES`` in the application's configuration and from the possible permissions
    of the different models.

    :return: A dictionary mapping a scope's object to its respective actions.
    """
    api_scopes = current_app.config["API_SCOPES"]
    results = {}

    for object_name in set(list(db.metadata.tables.keys()) + list(api_scopes.keys())):
        actions = []

        model = get_class_by_tablename(object_name)
        if model is not None:
            permissions = rgetattr(model, "Meta.permissions", {})

            for action, _ in permissions.get("global_actions", []) + permissions.get(
                "actions", []
            ):
                if action not in actions:
                    actions.append(action)

        for action in api_scopes.get(object_name, []):
            if action not in actions:
                actions.append(action)

        if actions:
            results[object_name] = actions

    return results


def create_pagination_data(total, page, per_page, endpoint, **kwargs):
    r"""Create pagination information for use in a JSON response.

    Since the pagination data will include links to the current, next and previous
    "pages", the necessary information to build said links needs to be given as well,
    i.e. the endpoint and its corresponding URL parameters.

    :param total: The total amount of items.
    :param page: The current page.
    :param per_page: Items per page.
    :param endpoint: The endpoint of the current request to build links to the current,
        next and previous page.
    :param \**kwargs: Additional keyword arguments to build the links with.
    :return: The pagination information as dictionary in the following form:

        .. code-block:: python3

            {
                "_pagination": {
                    "page": 2,
                    "per_page": 10,
                    "total_pages": 3,
                    "total_items": 25,
                    "_links": {
                        "prev": "https://...?page=1&...",
                        "self": "https://...?page=2&...",
                        "next": "https://...?page=3&...",
                    }
                }
            }

        The list of items is initially empty and can be filled afterwards with whatever
        data should be returned. Note that the links to the previous and next pages are
        only present if the respective page actually exists.
    """
    has_next = total > page * per_page
    has_prev = page > 1
    total_pages = math.ceil(total / per_page)

    url_args = {"endpoint": endpoint, "per_page": per_page, **kwargs}

    data = {
        "_pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total,
            "_links": {"self": url_for(page=page, **url_args)},
        },
    }

    if has_next:
        data["_pagination"]["_links"]["next"] = url_for(page=page + 1, **url_args)
    if has_prev:
        data["_pagination"]["_links"]["prev"] = url_for(page=page - 1, **url_args)

    return data
