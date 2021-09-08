#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------


class UpdateConnectorException(Exception):
    """
    Occurs when updating a connector call fails

    """
    def __init__(self, message):
        super().__init__(message)


class UpdateConnectionException(Exception):
    """
    Occurs when updating a connection call fails

    """
    def __init__(self, message):
        super().__init__(message)


class ConnectionCreationException(Exception):
    """
    Occurs when creation of connection fails

    """
    def __init__(self, message):
        super().__init__(message)
