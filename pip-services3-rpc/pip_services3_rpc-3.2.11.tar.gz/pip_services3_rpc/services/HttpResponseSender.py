# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpResponseSender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpResponseSender implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional

import bottle
from pip_services3_commons.convert.JsonConverter import JsonConverter
from pip_services3_commons.errors import ErrorDescriptionFactory


class HttpResponseSender:
    """
    Helper class that handles HTTP-based responses.
    """

    @staticmethod
    def send_result(result: Any) -> Optional[str]:
        """
        Creates a callback function that sends result as JSON object.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 200 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result
        :returns: JSON text response
        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return
        else:
            bottle.response.status = 200
            return JsonConverter.to_json(result)

    @staticmethod
    def send_empty_result(result: Any = None) -> Optional[str]:
        """
        Creates a callback function that sends an empty result with 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result:
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return JsonConverter.to_json(result)
        else:
            bottle.response.status = 404
            return

    @staticmethod
    def send_created_result(result: Any) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 201 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result or a promise with execution result
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return
        else:
            bottle.response.status = 201
            return JsonConverter.to_json(result)

    @staticmethod
    def send_deleted_result(result: Any = None) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 201 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result or a promise with execution result
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return

        bottle.response.status = 200
        return JsonConverter.to_json(result) if result else None

    @staticmethod
    def send_error(error: Any) -> str:
        """
        Sends error serialized as ErrorDescription object and appropriate HTTP status code. If status code is not defined, it uses 500 status code.

        :param error: an error object to be sent.

        :return: HTTP response status
        """
        basic_fillers = {'code': 'Undefined', 'status': 500, 'message': 'Unknown error',
                         'name': None, 'details': None,
                         'component': None, 'stack': None, 'cause': None}

        if error is None:
            error = type('error', (object,), basic_fillers)
        else:
            for k, v in basic_fillers.items():
                error.__dict__[k] = error.__dict__[k] if error.__dict__.get(k) is not None else v

        bottle.response.headers['Content-Type'] = 'application/json'
        error = ErrorDescriptionFactory.create(error)
        bottle.response.status = error.status
        return JsonConverter.to_json(error)
