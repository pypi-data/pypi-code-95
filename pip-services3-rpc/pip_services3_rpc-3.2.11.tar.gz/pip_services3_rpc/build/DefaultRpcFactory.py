# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.build.DefaultRpcFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DefaultRpcFactory implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from ..services import HttpEndpoint, StatusRestService, HeartbeatRestService


class DefaultRpcFactory(Factory):
    """
    Creates RPC components by their descriptors.
    """

    HttpEndpointDescriptor = Descriptor("pip-services", "endpoint", "http", "*", "1.0")
    StatusServiceDescriptor = Descriptor("pip-services", "status-service", "http", "*", "1.0")
    HeartbeatServiceDescriptor = Descriptor("pip-services", "heartbeat-service", "http", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super(DefaultRpcFactory, self).__init__()
        self.register_as_type(self.HttpEndpointDescriptor, HttpEndpoint)
        self.register_as_type(self.StatusServiceDescriptor, StatusRestService)
        self.register_as_type(self.HeartbeatServiceDescriptor, HeartbeatRestService)
