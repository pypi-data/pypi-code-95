# btrdb_admin.conn
# Module providing connection objects for BTrDB
#
# Author:   Allen Leis <allen@pingthings.io>
# Created:  Wed Mar 27 18:03:19 2019 -0400
#
# For license information, see LICENSE.txt
# ID: conn.py [] allen@pingthings.io $


"""
Module providing connection objects for BTrDB
"""

##########################################################################
## Imports
##########################################################################

import os

from btrdb_admin.acl import ACLAPI
from btrdb_admin.core import CoreAPI
from btrdb_admin.ingress import IngressAPI
from btrdb_admin.auth import BasicAuth
from btrdb_admin.grpcinterface import admin_pb2_grpc

import grpc # import last
from btrdb_admin.utils import header_manipulator_client_interceptor as hmci

##########################################################################
## Helpers
##########################################################################

def _root_certs():
    # grpc bundles its own CA certs which will work for all normal SSL
    # certificates but will fail for custom CA certs. Allow the user
    # to specify a CA bundle via env var to overcome this
    ca_bundle = os.getenv("BTRDB_CA_BUNDLE","")
    if ca_bundle != "":
        with open(ca_bundle, "rb") as f:
            return f.read()
    return None


##########################################################################
## Endpoint Connection
##########################################################################

class AdminAPI(ACLAPI, CoreAPI, IngressAPI):
    """
    Maintains the channel and stub gRPC client and acts as the serialization
    intermediary for server communications. For testing, connect and close can
    be mocked as well as the underlying client object.

    Parameters
    ----------
    endpoint : str
        The address of the adminapi to connect to, e.g. admin.predictivegrid.com:4411

    username : str
        The username identifying the authorized admin user.

    password : str
        The password authenticating the authorized admin user.
    """

    def __init__(self, endpoint, username=None, password=None):
        if len(endpoint.split(":")) != 2:
            raise ValueError("expecting address:port")

        self.client = None
        self.endpoint = endpoint

        self._channel = None
        if username and password:
            self.connect(username, password)

    def connect(self, username, password):
        certs = _root_certs()
        auth = BasicAuth(username, password)

        self._channel = grpc.secure_channel(
            self.endpoint,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(certs),
                grpc.metadata_call_credentials(auth, name="basic auth")
            )
        )

        if "JESTER_TOKEN" in os.environ:
            # header name must be lowercase
            interceptor = hmci.header_adder_interceptor("jester_token", os.environ.get("JESTER_TOKEN"))
            self._channel = grpc.intercept_channel(self._channel, interceptor)

        self.client = admin_pb2_grpc.AdminAPIStub(self._channel)

    def close(self):
        if not self._channel:
            return

        self._channel.close()
        self._channel = None
        self.client = None
