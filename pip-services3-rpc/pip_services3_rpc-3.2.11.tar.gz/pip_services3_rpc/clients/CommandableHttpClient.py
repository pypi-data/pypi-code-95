# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.clients.CommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Commandable HTTP client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Any, Optional

from .RestClient import RestClient


class CommandableHttpClient(RestClient, ABC):
    """
    Abstract client that calls commandable HTTP service.
    Commandable services are generated automatically for ICommandable objects. Each command is exposed as POST operation that receives all parameters in body object.

    ### Configuration parameters ###
        - base_route:              base route for remote URI
        - connection(s):
            - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
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

        class MyCommandableHttpClient(CommandableHttpClient, IMyClient):
            # ...

            def get_data(self, correlation_id, id):
                return self.call_command("get_data", correlation_id, MyData(id))

            # ...

        client = MyCommandableHttpClient()
        client.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                 "connection.host", "localhost",
                                                 "connection.port", 8080))
        data = client.getData("123", "1")
        # ...
    """

    def __init__(self, base_route: str):
        """
        Creates a new instance of the client.

        :param base_route: a base route for remote service.
        """
        super(CommandableHttpClient, self).__init__()
        self._base_route = base_route

    def call_command(self, name: str, correlation_id: Optional[str], params: Any) -> Any:
        """
        Calls a remote method via HTTP commadable protocol. The call is made via POST operation and all parameters are sent in body object. The complete route to remote method is defined as baseRoute + "/" + name.

        :param name: a name of the command to call.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param params: command parameters.

        :return: result of the command.
        """
        timing = self._instrument(correlation_id, self._base_route + '.' + name)
        try:
            # route = self.__fix_route(self._base_route) + self.__fix_route(name)
            # if self._base_route and self._base_route[0] != '/':
            #     route = '/'  + self._base_route + '/' + name
            # else:
            #     route = self._base_route + '/' + name
            return self._call('POST', name, correlation_id, None, params)
        except Exception as err:
            timing.end_failure(err)
        finally:
            timing.end_timing()
