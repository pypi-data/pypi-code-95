# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import abc

import collections

import os.path
import pathlib

import requests_async as requests

###############################################################
#
#   REFINITIV IMPORTS
#

from ....errors import EnvError

###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASS DEFINITIONS
#

#   namedtuple for stream service information
StreamServiceInformation = collections.namedtuple(
    "StreamServiceInformation",
    ["scheme", "host", "port", "path", "data_formats", "location"],
)


class StreamServiceDiscoveryHandler(abc.ABC):
    """this class is designed for handle the difference kind of service discovery endpoint.
    i.e. the service discovery of data api proxy, RDP streaming price service discovery, etc.
    """

    def __init__(self, session, stream_discovery_endpoint_url, **kwargs):
        self._session = session
        self._stream_discovery_endpoint_url = stream_discovery_endpoint_url

    async def get_stream_service_information(self):
        """do a process for getting an stream service information from service discovery endpoint"""

        #   do request to service discovery
        service_discovery_response = await self._request_to_service_discovery()

        #   process the service discovery response
        stream_service_information = self._process_service_discovery_response(
            service_discovery_response
        )

        #   do filter by the specific location from config file
        stream_service_information = self._filter_stream_services_by_location(
            stream_service_information
        )

        #   done
        return stream_service_information

    async def _request_to_service_discovery(self):
        """make a request to the service discovery"""
        self._session.debug(
            f"request to stream service discovery {self._stream_discovery_endpoint_url}"
        )

        #   request to service discovery endpoint
        service_discovery_response = await self._session.http_request_async(
            self._stream_discovery_endpoint_url
        )

        if service_discovery_response.status_code != requests.codes.ok:
            raise EnvError(
                service_discovery_response.status_code,
                f"\nRequest to stream service discovery {self._stream_discovery_endpoint_url}"
                f" ended with:\n"
                f"    Staus code: {service_discovery_response.status_code}\n"
                f"    Message: {service_discovery_response.text}",
            )

        #   done, extract and build the endpoint services from discovery endpoint response
        return service_discovery_response.json()

    def _filter_stream_services_by_location(self, stream_service_information):
        """filter the stream service by the specific location from config file."""
        return stream_service_information

    @abc.abstractmethod
    def _process_service_discovery_response(self, service_discovery_response):
        """this is a method to handle each of differnce kind of service discovery"""
        pass

    def _extract_stream_service_info(self, service_item: dict):
        """this function is designed for parsing a single service from service discovery response.
                and build a stream connection information.

            service item example

                data api proxy
                http://localhost:9000/api/rdp/streaming/pricing/v1/
                {
                    "dataFormat":["tr_json2"],
                    "endpoint":"localhost/api/rdp/streaming/pricing/v1/WebSocket",
                    "location":["local"],
                    "port":9000,
                    "provider":"local",
                    "transport":"websocket"
                }

                or

                https://api.ppe.refinitiv.com/streaming/benchmark/v1/resource
                {
                    "provider": "AWS",
                    "endpoint": "ppe.benchmark.refinitiv.com/websocket",
                    "transport": "websocket",
                    "port": 443,
                    "dataFormat": [
                        "json"
                    ],
                    "location": [
                        "us-east-1"
                    ]
                }

                or

                https://api.ppe.refinitiv.com/streaming/pricing/v1/
                {
                    "port": 443,
                    "location": [
                        "ap-southeast-1a"
                    ],
                    "transport": "websocket",
                    "provider": "aws",
                    "endpoint": "a205464-p1-sm-quest-it-d6e8fb256247b086.elb.ap-southeast-1.amazonaws.com",
                    "dataFormat": [
                        "tr_json2"
                    ]
                }

        Returns
        -------
        obj
            transport, host, port, path, data_format, location
        """

        #   check the require websocket endpoint information

        #       endpoint
        endpoint = service_item.get("endpoint", None)
        assert endpoint is not None

        #       port
        port = service_item.get("port", None)
        assert port is not None

        #       data format
        data_format = service_item.get("dataFormat", None)
        assert data_format is not None
        assert isinstance(data_format, list)

        #       transport
        transport = service_item.get("transport", None)
        assert transport is not None
        assert isinstance(transport, str)
        # assert transport == 'websocket'

        #       location
        location = service_item.get("location", None)
        assert location is not None

        #   build the StreamServiceInformation object
        #       do a parsing on endpoint determine the host and path
        endpoint_path = pathlib.Path(endpoint)
        assert len(endpoint_path.parts) >= 1

        #   extract host, path
        host = str(endpoint_path.parts[0])
        if len(endpoint_path.parts) > 1:
            #   it has a path
            path = "/".join(endpoint_path.parts[1:])
        else:
            #   it doesn't has a path
            path = None

        #   done
        return transport, host, port, path, data_format, location


class DesktopStreamServiceDiscoveryHandler(StreamServiceDiscoveryHandler):
    """this class is designed for handling a data api proxy service discovery"""

    def __init__(self, session, stream_discovery_endpoint_url, **kwargs):
        StreamServiceDiscoveryHandler.__init__(
            self, session, stream_discovery_endpoint_url, **kwargs
        )

    def _process_service_discovery_response(self, service_discovery_response):
        """this is a method to handle each of difference kind of service discovery

        response example
            {
                "services":[
                    {
                        "dataFormat":["tr_json2"],
                        "endpoint":"localhost/api/rdp/streaming/pricing/v1/WebSocket",
                        "location":["local"],
                        "port":9000,
                        "provider":"local",
                        "transport":"websocket"
                    }
                ]
            }

        """
        #   extract and validate response

        #   extract the WebSocket endpoint
        services = service_discovery_response.get("services", None)
        assert services is not None
        assert isinstance(services, list)

        #   for the data api proxy, it should only has one WebSocket endpoint
        assert (
            len(services) == 1
        ), f"ERROR!!! CANNOT retreive streaming endpoint from discovery endpoint ({self._stream_discovery_endpoint_url})\n    Please check your DATA API Proxy."
        service = services[0]
        assert isinstance(service, dict)

        #   extract the service item
        stream_service_info = self._get_stream_service_info(service)

        #   done
        return [
            stream_service_info,
        ]

    def _get_stream_service_info(self, service_item: dict):
        """this funciton is desinged for parsing a single service from service discovery response.
                and build a stream connection information.

            service item example
                {
                    "dataFormat":["tr_json2"],
                    "endpoint":"localhost/api/rdp/streaming/pricing/v1/WebSocket",
                    "location":["local"],
                    "port":9000,
                    "provider":"local",
                    "transport":"websocket"
                }

        Returns
        -------
        obj
            stream connection item.
        """
        #   extract information by using parent class function
        (
            transport,
            host,
            port,
            path,
            data_formats,
            location,
        ) = StreamServiceDiscoveryHandler._extract_stream_service_info(
            self, service_item
        )
        assert transport == "websocket"

        #   build the stream service information
        return StreamServiceInformation(
            scheme="ws",
            host=host,
            port=port,
            path=path,
            data_formats=data_formats,
            location=location,
        )


class PlatformStreamServiceDiscoveryHandler(StreamServiceDiscoveryHandler):
    """this class is designed for handling RDP platform streaming service discovery"""

    def __init__(
        self,
        session,
        stream_discovery_endpoint_url,
        prefer_stream_service_locations: list = None,
        **kwargs,
    ):
        StreamServiceDiscoveryHandler.__init__(
            self, session, stream_discovery_endpoint_url, **kwargs
        )
        self._prefer_stream_service_locations = (
            prefer_stream_service_locations
            if prefer_stream_service_locations is not None
            else []
        )

    def _filter_stream_services_by_location(self, stream_service_information: list):
        """override the filter the stream service by the specific location from config file."""

        assert isinstance(self._prefer_stream_service_locations, list)
        assert stream_service_information is not None and isinstance(
            stream_service_information, list
        )

        #   filter by multiple AZ
        multi_az_stream_service_information = []
        for stream_service in stream_service_information:
            if len(stream_service.location) > 1:
                #   this service has multiple AZ, so use it
                multi_az_stream_service_information.append(stream_service)
        self._session.debug(
            f"multiple AZ stream services = {multi_az_stream_service_information}"
        )

        #   if no multiple AZ available, use the single AZ instread
        available_stream_service_information = multi_az_stream_service_information
        if len(multi_az_stream_service_information) == 0:
            #   use the single AZ instread because no multiple AZ available
            self._session.debug(
                f"#WARNING no multiple AZ available for the stream [{self._stream_discovery_endpoint_url}]"
            )
            available_stream_service_information = stream_service_information

        #   filter and build a prefer websocket service based on location
        #   check the prefer location is specify or not?
        if len(self._prefer_stream_service_locations) == 0:
            #   no prefer location, so don't filter
            return available_stream_service_information

        #   build the prefer stream services
        prefer_stream_service_infos = []
        for prefer_stream_service_location in self._prefer_stream_service_locations:

            #   list all location start with the prefer location name
            stream_service_matched_location = []
            for stream_service in available_stream_service_information:

                #   check the locations
                for location in stream_service.location:
                    if location.startswith(prefer_stream_service_location):
                        #   matched location with prefer location

                        #   store the matched location
                        stream_service_matched_location.append(stream_service)

                        #   store as prefer location
                        prefer_stream_service_infos.append(stream_service)

                        #   done for this stream service
                        break

            #   remove matched location
            if len(stream_service_matched_location) == 0:
                #   invalid prefer location in config file
                raise ValueError(
                    f"ERROR!!! Invalid location {prefer_stream_service_location} that specify in config file."
                )

        #   done
        return prefer_stream_service_infos

    def _process_service_discovery_response(self, service_discovery_response):
        """this is a method to handle each of difference kind of service discovery

        response example

            https://api.ppe.refinitiv.com/streaming/benchmark/v1/resource
            {
                "provider": "AWS",
                "endpoint": "ppe.benchmark.refinitiv.com/websocket",
                "transport": "websocket",
                "port": 443,
                "dataFormat": [
                    "json"
                ],
                "location": [
                    "us-east-1"
                ]
            }

            or

            https://api.ppe.refinitiv.com/streaming/pricing/v1/
            {
                "port": 443,
                "location": [
                    "ap-southeast-1a"
                ],
                "transport": "websocket",
                "provider": "aws",
                "endpoint": "a205464-p1-sm-quest-it-d6e8fb256247b086.elb.ap-southeast-1.amazonaws.com",
                "dataFormat": [
                    "tr_json2"
                ]
            }

        """
        #   extract and validate response

        #   extract the WebSocket endpoint
        services = service_discovery_response.get("services", None)
        assert services is not None
        assert isinstance(services, list)

        #   for the data api proxy, it should only has one WebSocket endpoint
        assert len(services) > 0

        #   loop over all stream service endpoint
        stream_service_infos = []
        for service in services:
            assert isinstance(service, dict)

            #   extract the service item
            stream_service_info = self._get_stream_service_info(service)

            #   store the valid stream service
            if stream_service_info is not None:
                #   valid websocket stream service
                stream_service_infos.append(stream_service_info)

        #   done
        return stream_service_infos

    def _get_stream_service_info(self, service_item: dict):
        """this function is designed for parsing a single service from service discovery response.
                and build a stream connection information.

            service item example
                {
                    "provider": "AWS",
                    "endpoint": "ppe.benchmark.refinitiv.com/websocket",
                    "transport": "websocket",
                    "port": 443,
                    "dataFormat": [
                        "json"
                    ],
                    "location": [
                        "us-east-1"
                    ]
                }

        Returns
        -------
        obj
            stream connection item.
        """
        #   extract information by using parent class function
        (
            transport,
            host,
            port,
            path,
            data_formats,
            location,
        ) = StreamServiceDiscoveryHandler._extract_stream_service_info(
            self, service_item
        )

        #   filter only the WebSocket
        if transport != "websocket":
            #   skip this stream service information
            return None

        #   build the stream service information
        return StreamServiceInformation(
            scheme="wss",
            host=host,
            port=port,
            path=path,
            data_formats=data_formats,
            location=location,
        )
