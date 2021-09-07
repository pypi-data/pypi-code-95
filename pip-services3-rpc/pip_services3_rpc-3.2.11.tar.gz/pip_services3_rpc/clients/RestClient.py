# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.client.RestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    REST client implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
from typing import Optional, Any

import requests
from pip_services3_commons.config import ConfigParams, IConfigurable
from pip_services3_commons.data import PagingParams
from pip_services3_commons.errors import ErrorDescription, ApplicationExceptionFactory
from pip_services3_commons.errors import UnknownException, InvocationException
from pip_services3_commons.refer import IReferenceable, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger
from pip_services3_components.trace.CompositeTracer import CompositeTracer

from ..connect.HttpConnectionResolver import HttpConnectionResolver
from ..services.InstrumentTiming import InstrumentTiming


class RestClient(IOpenable, IConfigurable, IReferenceable):
    """
    Abstract client that calls remove endpoints using HTTP/REST protocol.

    ### Configuration parameters ###
        - base_route:              base route for remote URI
        - connection(s):
            - discovery_key:         (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - protocol:              connection protocol: http or https
            - host:                  host name or IP address
            - port:                  port number
            - uri:                   resource URI or connection string with all parameters in it
        - options:
            - retries:               number of retries (default: 3)
            - connect_timeout:       connection timeout in milliseconds (default: 10 sec)
            - timeout:               invocation timeout in milliseconds (default: 10 sec)

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

    Example:

    .. code-block:: python

        class MyRestClient(RestClient, IMyClient):
            def get_data(self, correlation_id, id):
                timing = self.instrument(correlationId, 'myclient.get_data')
                result = self._controller.get_data(correlationId, id)
                timing.end_timing()
                return result

            # ...

        client = MyRestClient()
        client.configure(ConfigParams.fromTuples("connection.protocol", "http",
                                                 "connection.host", "localhost",
                                                 "connection.port", 8080))

        data = client.getData("123", "1")
        # ...
    """
    __default_config = ConfigParams.from_tuples(
        "connection.protocol", "http",
        "connection.host", "0.0.0.0",
        "connection.port", 3000,

        "options.timeout", 10000,
        "options.request_max_size", 1024 * 1024,
        "options.connect_timeout", 10000,
        "options.retries", 3,
        "options.debug", True
    )

    def __init__(self):
        """
        Creates a new instance of the client.
        """
        # The HTTP client.
        self._client: Any = None
        # The remote service uri which is calculated on open.
        self._uri: str = None
        # The invocation timeout in milliseconds.
        self._timeout = 1000
        # The connection resolver.
        self._connection_resolver: HttpConnectionResolver = HttpConnectionResolver()
        # The logger.
        self._logger: CompositeLogger = CompositeLogger()
        # The performance counters.
        self._counters: CompositeCounters = CompositeCounters()
        # The tracer.
        self._tracer: CompositeTracer = CompositeTracer()
        # The configuration options.
        self._options: ConfigParams = ConfigParams()
        # The base route.
        self._base_route: str = None
        # The number of retries.
        self._retries = 1
        # The default headers to be added to every request.
        self._headers: dict = {}
        # The connection timeout in milliseconds.
        self._connect_timeout = 1000

        self._correlation_id_location: str = "query"

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._tracer.set_references(references)
        self._connection_resolver.set_references(references)

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self.__default_config)
        self._connection_resolver.configure(config)

        self._options.override(config.get_section("options"))
        self._retries = config.get_as_integer_with_default("options.retries", self._retries)
        self._connect_timeout = config.get_as_integer_with_default("options.connect_timeout", self._connect_timeout)
        self._timeout = config.get_as_integer_with_default("options.timeout", self._timeout)

        self._base_route = config.get_as_string_with_default("base_route", self._base_route)
        self._correlation_id_location = config.get_as_string_with_default("options.correlation_id_place",
                                                                          self._correlation_id_location)
        self._correlation_id_location = config.get_as_string_with_default("options.correlation_id",
                                                                          self._correlation_id_location)

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: InstrumentTiming object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Calling %s method", name)
        self._counters.increment_one(name + ".call_count")

        counter_timing = self._counters.begin_timing(name + '.call_time')
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, "call",
                                self._logger, self._counters, counter_timing, trace_timing)

    # def _instrument_error(self, correlation_id, name, err, result=None, callback=None):
    #     """
    #     Adds instrumentation to error handling.
    #
    #     :param correlation_id: (optional) transaction id to trace execution through call chain.
    #     :param name: a method name.
    #     :param err: an occured error
    #     :param result: (optional) an execution result
    #     :param callback: (optional) an execution callback
    #     """
    #     if err is not None:
    #         TYPE_NAME = self.__class__.__name__ or 'unknown-target'
    #         self.__logger.error(correlation_id, err, f"Failed to call {name} method of {TYPE_NAME}")
    #         self.__counters.increment_one(f"{name}.call_errors")
    #     if callback:
    #         callback(err, result)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._client is not None

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_open():
            return

        connection = self._connection_resolver.resolve(correlation_id)

        self._uri = connection.get_as_string('uri')

        self._client = requests

        self._logger.debug(correlation_id, "Connected via REST to " + self._uri)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._client is not None:
            self._logger.debug(correlation_id, "Disconnected from " + self._uri)

        self._client = None
        self._uri = None

    def _to_json(self, obj):
        if obj is None:
            return None

        if isinstance(obj, set):
            obj = list(obj)
        if isinstance(obj, list):
            result = []
            for item in obj:
                item = self._to_json(item)
                result.append(item)
            return result

        if isinstance(obj, dict):
            result = {}
            for (k, v) in obj.items():
                v = self._to_json(v)
                result[k] = v
            return result

        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, '__dict__'):
            return self._to_json(obj.__dict__)
        return obj

    def fix_route(self, route) -> str:
        if route is not None and len(route) > 0:
            if route[0] != '/':
                route = f'/{route}'
            return route

        return ''

    def __create_request_route(self, route: str) -> str:
        builder = ''
        if self._uri is not None and len(self._uri) > 0:
            builder = self._uri

            builder += self.fix_route(self._base_route)

        if route[0] != '/':
            builder += '/'
        builder += route

        return builder

    def add_correlation_id(self, params: Any = None, correlation_id: Optional[str] = None) -> Any:
        """
        Adds a correlation id (correlation_id) to invocation parameter map.

        :param params: invocation parameters.
        :param correlation_id: (optional) a correlation id to be added.

        :returns: invocation parameters with added correlation id.

        """
        params = params or {}
        if not (correlation_id is None):
            params['correlation_id'] = correlation_id

        return params

    def _add_filter_params(self, params: Any = None, filters: Any = None) -> dict:
        """
        Adds filter parameters (with the same name as they defined)
        to invocation parameter map.

        :param params:  invocation parameters.
        :param filters: (optional) filter parameters
        :returns: invocation parameters with added filter parameters.
        """
        params = params or {}
        if not (filters is None):
            params.update(filters)

        return params

    def _add_paging_params(self, params: dict = None, paging: PagingParams = None) -> dict:
        """
        Adds paging parameters (skip, take, total) to invocation parameter map.


        :param params: invocation parameters.
        :param paging: (optional) paging parameters

        :returns: invocation parameters with added paging parameters.

        """
        params = params or {}
        if paging:
            if paging.total:
                params['total'] = paging.total
            if paging.skip:
                params['skip'] = paging.skip
            if paging.take:
                params['take'] = paging.take

        return params

    def _call(self, method: str, route: str, correlation_id: Optional[str] = None, params: dict = None,
              data: Any = None) -> Any:
        """
        Calls a remote method via HTTP/REST protocol.

        :param method: HTTP method: "get", "head", "post", "put", "delete"

        :param route: a command route. Base route will be added to this route

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param params: (optional) query parameters.

        :param data: (optional) body object.

        :return: result object
        """
        method = method.upper()

        if method not in ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'PATCH']:
            raise UnknownException(correlation_id, 'UNSUPPORTED_METHOD',
                                   'Method is not supported by REST client').with_details('verb', method)

        route = self.__create_request_route(route)
        params = self.add_correlation_id(correlation_id=correlation_id, params=params)
        response = None
        result = None

        if self._correlation_id_location == 'query' or self._correlation_id_location == 'both':
            params = self.add_correlation_id(params, correlation_id)

        if self._correlation_id_location == 'headers' or self._correlation_id_location == 'both':
            self._headers['correlation_id'] = correlation_id

        try:
            # Call the service
            data = data if isinstance(data, str) else self._to_json(data)
            response = requests.request(method, route,
                                        headers=self._headers,
                                        json=data,
                                        params=params,
                                        timeout=self._timeout)

        except Exception as ex:
            error = InvocationException(correlation_id, 'REST_ERROR', 'REST operation failed: ' + str(ex)).wrap(ex)
            raise error

        if response.status_code == 204:
            return None

        try:
            # Retrieve JSON data
            if response.content:
                result = response.json()
            else:
                result = None
        except:
            # Data is not in JSON
            if response.status_code < 400:
                raise UnknownException(correlation_id, 'FORMAT_ERROR',
                                       'Failed to deserialize JSON data: ' + response.text) \
                    .with_details('response', response.text)
            else:
                raise UnknownException(correlation_id, 'UNKNOWN', 'Unknown error occured: ' + response.text) \
                    .with_details('response', response.text)

        # Return result
        if response.status_code < 400:
            return result

        # Raise error
        # Todo: We need to implement proper from_value method
        error = ErrorDescription.from_json(result)
        error.status = response.status_code

        raise ApplicationExceptionFactory.create(error)
