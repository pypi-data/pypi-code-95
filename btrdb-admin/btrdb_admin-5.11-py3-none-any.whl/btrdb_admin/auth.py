# btrdb.admin.auth
# gRPC basic auth metadata plugin
#
# Author:   PingThings
# Created:  Mon Oct 07 13:46:16 2019 -0400
#
# For license information, see LICENSE.txt
# ID: auth.py [] benjamin@pingthings.io $

"""
gRPC basic auth metadata plugin
"""

##########################################################################
## Imports
##########################################################################

import grpc
import base64


HEADER_KEY = "authorization"


class BasicAuth(grpc.AuthMetadataPlugin):
    """
    A custom gRPC authentication mechanism that implements basic auth.

    Parameters
    ----------
    username : str
        the username of the authenticating user.

    password : str
        the password of the authenticating user.
    """

    def __init__(self, username, password):
        # Stores the authorization as the b64 encoded header value
        auth = base64.b64encode(
            "{}:{}".format(username, password).encode("utf-8")
        )
        self.__authorization = "basic {}".format(auth.decode("ascii"))

    def __call__(self, context, callback):
        """Implements authentication by passing metadata to a callback.

        Implementations of this method must not block.

        Parameters
        ----------
        context:
            An AuthMetadataContext providing information on the RPC that
            the plugin is being called to authenticate.

        callback:
            An AuthMetadataPluginCallback to be invoked either synchronously
            or asynchronously.
        """
        callback(((HEADER_KEY, self.__authorization),), None)
