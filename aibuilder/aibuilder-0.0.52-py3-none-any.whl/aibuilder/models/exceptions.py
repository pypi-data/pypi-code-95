#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

class SchemaValidationException(Exception):
    """
    The exception class used for schema validation pre check errors.

    """
    def __init__(self, message):
        super().__init__(message)


class DataBindingValidationException(Exception):
    """
    The exception class used for data binding validation

    """
    def __init__(self, message):
        super().__init__(message)
