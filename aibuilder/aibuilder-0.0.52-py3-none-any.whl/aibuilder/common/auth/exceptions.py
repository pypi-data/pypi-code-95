#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

class ConfigDirectoryCreationException(Exception):
    """
    Occurs when config directory cannot be created

    """
    def __init__(self, message):
        super().__init__(message)


class ConfigFileNotFoundException(ValueError):
    """
    When config file not found

    """
    def __init__(self, message):
        super().__init__(message)
