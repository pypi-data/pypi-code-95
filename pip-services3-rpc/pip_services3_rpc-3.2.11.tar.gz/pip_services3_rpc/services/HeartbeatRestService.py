# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HeartbeatRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Heartbeat rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime
from typing import Callable

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.convert import StringConverter

from .RestService import RestService


class HeartbeatRestService(RestService):
    """
    Service returns heartbeat via HTTP/REST protocol.The service responds on /heartbeat route (can be changed) with a string with the current time in UTC. This service route can be used to health checks by loadbalancers and container orchestrators.

    ### Configuration parameters ###
        - base_route:              base route for remote URI (default: "")
        - route:                   route to heartbeat operation (default: "heartbeat")
        - dependencies:
            - endpoint:              override for HTTP Endpoint dependency
        - connection(s):
        - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
        - protocol:              connection protocol: http or https
        - host:                  host name or IP address
        - port:                  port number
        - uri:                   resource URI or connection string with all parameters in it

    ### References ###
        - `*:logger:*:*:1.0`         (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`       (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`      (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:endpoint:http:*:1.0`    (optional) :class:`HttpEndpoint <pip_services3_rpc.services.HttpEndpoint>` reference

    Example:
    
    .. code-block:: python

          service = HeartbeatService()
          service.configure(ConfigParams.from_tuples("route", "ping",
                                                     "connection.protocol", "http",
                                                     "connection.host", "localhost",
                                                     "connection.port", 8080))

          service.open("123")
          # ...
    """

    def __init__(self):
        """
        Creates a new instance of this service.
        """
        super(HeartbeatRestService, self).__init__()
        self.__route = "heartbeat"

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super(HeartbeatRestService, self).configure(config)
        self.__route = config.get_as_string_with_default("route", self.__route)

    def register(self):
        """
        Registers all service routes in HTTP endpoint.
        """
        self.register_route("GET", self.__route, None, self.heartbeat)

    def heartbeat(self) -> str:
        """
        Handles heartbeat requests

        :return: http response to the request.
        """
        result = StringConverter.to_string(datetime.datetime.now())
        return self.send_result(result)
