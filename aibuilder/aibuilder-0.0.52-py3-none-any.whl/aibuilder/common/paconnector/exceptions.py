#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

class DuplicateModelException(Exception):
    """
    Occurs when a model with the same name already exists

    """
    def __init__(self, message):
        super().__init__(message)


class RequestFormatException(Exception):
    """
    Occurs when the response is a 400 error

    """
    def __init__(self, message):
        super().__init__(message)
