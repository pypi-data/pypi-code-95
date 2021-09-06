# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.RestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import json
from abc import abstractmethod
from typing import Optional, Any, Callable

import bottle
from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import InvalidStateException
from pip_services3_commons.refer import IReferenceable, DependencyResolver, IUnreferenceable, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger
from pip_services3_components.trace.CompositeTracer import CompositeTracer

from .HttpEndpoint import HttpEndpoint
from .HttpResponseSender import HttpResponseSender
from .IRegisterable import IRegisterable
from .ISwaggerService import ISwaggerService
from .InstrumentTiming import InstrumentTiming


class RestService(IOpenable, IConfigurable, IReferenceable, IUnreferenceable, IRegisterable):
    """
    Abstract service that receives remove calls via HTTP/REST protocol.

    ### Configuration parameters ###
        - base_route:              base route for remote URI
        - dependencies:
            - endpoint:              override for HTTP Endpoint dependency
            - controller:            override for Controller dependency
        - connection(s):
            - discovery_key:         (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - protocol:              connection protocol: http or https
            - host:                  host name or IP address
            - port:                  port number
            - uri:                   resource URI or connection string with all parameters in it
        - credential - the HTTPS credentials:
            - ssl_key_file:         the SSL private key in PEM
            - ssl_crt_file:         the SSL certificate in PEM
            - ssl_ca_file:          the certificate authorities (root cerfiticates) in PEM

    ### References ###
        - `*:logger:*:*:1.0`         (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`       (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`      (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:endpoint:http:*:1.0`    (optional) :class:`HttpEndpoint <pip_services3_rpc.services.HttpEndpoint>` reference
        - `*:tracer:*:*:1.0`         (optional) :class:`ITracer <pip_services3_components.trace.ITracer.ITracer>` components to record traces

    Example:

    .. code-block:: python

        class MyRestService(RestService):
            _controller = None
            # ...

            def __init__(self):
                super(MyRestService, self).__init__()
                self._dependencyResolver.put("controller", Descriptor("mygroup","controller","*","*","1.0"))

            def set_references(self, references):
                super(MyRestService, self).set_references(references)
                self._controller = self._dependencyResolver.get_required("controller")

            def register():
                # ...

        service = MyRestService()
        service.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                       "connection.host", "localhost",
                                                       "connection.port", 8080))
        service.set_references(References.from_tuples(Descriptor("mygroup","controller","default","default","1.0"), controller))
        service.open("123")
    """
    _default_config = ConfigParams.from_tuples("base_route", None,
                                               "dependencies.endpoint", "*:endpoint:http:*:1.0",
                                               "dependencies.swagger", "*:swagger-service:*:*:1.0")

    def __init__(self):

        # The dependency resolver.
        self._dependency_resolver: DependencyResolver = DependencyResolver(self._default_config)
        # The logger.
        self._logger: CompositeLogger = CompositeLogger()
        # The performance counters.
        self._counters: CompositeCounters = CompositeCounters()
        self._debug = False
        # The base route.
        self._base_route: str = None
        # The HTTP endpoint that exposes this service.
        self._endpoint: HttpEndpoint = None
        # The tracer.
        self._tracer: CompositeTracer = CompositeTracer()

        self._config: ConfigParams = None
        self._swagger_service: ISwaggerService = None
        self._swagger_enabled = False
        self._swagger_route = 'swagger'

        self.__local_endpoint: bool = None
        self.__references: IReferences = None
        self.__opened: bool = None

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__references = references
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)
        self._endpoint = self._dependency_resolver.get_one_optional('endpoint')

        if self._endpoint is None:
            self._endpoint = self.create_endpoint()
            self.__local_endpoint = True
        else:
            self.__local_endpoint = False

        self._endpoint.register(self)

        self._swagger_service = self._dependency_resolver.get_one_optional('swagger')

    def unset_references(self):
        """
        Unsets (clears) previously set references to dependent components.
        """
        if not (self._endpoint is None):
            self._endpoint.unregister(self)
            self._endpoint = None

        self._swagger_service = None

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self._default_config)
        self._config = config
        self._dependency_resolver.configure(config)
        self._base_route = config.get_as_string_with_default("base_route", self._base_route)

        self._swagger_enabled = self._config.get_as_boolean_with_default("swagger.enable", self._swagger_enabled)
        self._swagger_route = self._config.get_as_string_with_default("swagger.route", self._swagger_route)

    def create_endpoint(self):
        endpoint = HttpEndpoint()
        if not (self._config is None):
            endpoint.configure(self._config)

        if not (self.__references is None):
            endpoint.set_references(self.__references)

        return endpoint

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: InstrumentTiming object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Executing %s method", name)
        self._counters.increment_one(name + ".exec_count")

        counter_timing = self._counters.begin_timing(name + ".exec_time")
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, "call",
                                self._logger, self._counters, counter_timing, trace_timing)

    # def _instrument_error(self, correlation_id, name, error, result, callback):
    #     if not (error is None):
    #         self._logger.error(correlation_id, error, f"Failed to execute {name} method")
    #         self._counters.increment_one(f"{name}.exec_error")
    #     if not (callback is None):
    #         callback(error, result)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """

        if self.is_open():
            return

        if self._endpoint is None:
            self._endpoint = self.create_endpoint()
            self._endpoint.register(self)
            self.__local_endpoint = True

        if self.__local_endpoint:
            self._endpoint.open(correlation_id)

        self.__opened = True
        # # register route
        # if self._registered != True:
        #     self.add_route()
        #     self._registered = True

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if not self.__opened:
            return

        if self._endpoint is None:
            raise InvalidStateException(correlation_id, "NO_ENDPOINT", "HTTP endpoint is missing")

        if self.__local_endpoint:
            self._endpoint.close(correlation_id)

        self.__opened = False

    def send_result(self, result: Any) -> Optional[str]:
        """
        Creates a callback function that sends result as JSON object. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 200 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :param result: a body object to result.

        :return: execution result.
        """

        return HttpResponseSender.send_result(result)

    def send_created_result(self, result: Any) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 201 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :param result: a body object to result.

        :return: execution result.
        """
        return HttpResponseSender.send_created_result(result)

    def send_deleted_result(self, result: Any = None) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 200 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :param result: a body object to result.
        :return: execution result.
        """

        return HttpResponseSender.send_deleted_result(result)

    def send_error(self, error: Any) -> str:
        """
        Sends error serialized as ErrorDescription object and appropriate HTTP status code. If status code is not defined, it uses 500 status code.

        :param error: an error object to be sent.
        """

        return HttpResponseSender.send_error(error)

    def fix_route(self, route) -> str:
        if route is not None and len(route) > 0:
            if route[0] != '/':
                route = f'/{route}'
            return route

        return ''

    def register_route(self, method: str, route: str, schema: Optional[Schema], handler: Callable):
        """
        Registers an action in this objects REST server (service) by the given method and route.

        :param method: the HTTP method of the route.

        :param route: the route to register in this object's REST server (service).

        :param schema: the schema to use for parameter validation.

        :param handler: the action to perform at the given route.
        """
        if self._endpoint is None:
            return

        route = f"{self.fix_route(self._base_route)}{self.fix_route(route)}"
        # if not (self._base_route is None) and len(self._base_route) > 0:
        #     base_route = self._base_route
        #     if base_route[0] != '/':
        #         base_route = '/' + base_route
        #     if route[0] != '/':
        #         base_route = base_route + '/'
        #     route = base_route + route
        self._endpoint.register_route(method, route, schema, handler)

    @abstractmethod
    def register(self):
        """
        Registers all service routes in HTTP endpoint.

        This method is called by the service and must be overriden
        in child classes.
        """

    def _get_data(self) -> dict:
        data = bottle.request.json
        if isinstance(data, str):
            return json.loads(bottle.request.json)
        elif bottle.request.json:
            return bottle.request.json
        else:
            return {}

    def _append_base_route(self, route):
        route = route or ''

        if self._base_route is not None and len(self._base_route) > 0:
            base_route = self._base_route
            if base_route[0] != '/':
                base_route = '/' + base_route
                route = base_route + route
        return route

    def register_route_with_auth(self, method: str, route: str, schema: Schema, authorize: Callable, action: Callable):
        """
        Registers a route with authorization in HTTP endpoint.

        :param method: HTTP method: "get", "head", "post", "put", "delete"
        :param route: a command route. Base route will be added to this route
        :param schema: a validation schema to validate received parameters.
        :param authorize: an authorization interceptor
        :param action: an action function that is called when operation is invoked.
        """
        if self._endpoint is None:
            return

        route = self._append_base_route(self.fix_route(route))

        self._endpoint.register_route_with_auth(method, route, schema, authorize, action)

    def register_interceptor(self, route: str, action: Callable):
        """
        Registers a middleware for a given route in HTTP endpoint.

        :param route: a command route. Base route will be added to this route
        :param action: an action function that is called when middleware is invoked.
        """
        if self._endpoint is None:
            return

        route = self._append_base_route(self.fix_route(route))

        self._endpoint.register_interceptor(route, action)

    def _register_open_api_spec_from_file(self, path: str):
        with open(path, 'r') as f:
            content = f.read()
        self._register_open_api_spec(content)

    def _register_open_api_spec(self, content: str):

        def handler():
            bottle.response.headers.update({
                'Content-Length': len(content.encode('utf-8')),
                'Content-Type': 'application/x-yaml'
            })

            return content

        if self._swagger_enabled:
            self.register_route('GET', self._swagger_route, None, handler)

            if self._swagger_service is not None:
                self._swagger_service.register_open_api_spec(self._base_route, self._swagger_route)

    def _get_correlation_id(self) -> Optional[str]:
        """
        Returns correlationId from request

        :returns: Returns correlationId from request
        """
        correlation_id = bottle.request.query.get('correlation_id')
        if correlation_id is None or correlation_id == '':
            correlation_id = bottle.request.headers.get('correlation_id')
        return correlation_id
