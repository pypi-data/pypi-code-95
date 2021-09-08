#  -----------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License in the project root for
#  license information.
#  -----------------------------------------------------------------------------

class SchemaValidationException(Exception):
    """
    The exception class used for data quality pre check errors.

    """
    def __init__(self, message):
        super().__init__(message)


class RegistrationException(Exception):
    """
    Any exception when registering a model

    """
    def __init__(self, message):
        super().__init__(message)


class ModelNotFoundException(Exception):
    """
    Occurs when model cannot be found with specified name

    """
    def __init__(self, message):
        super().__init__(message)


class DataSpecException(Exception):
    """
    Occurs during creation of the model run data specification

    """
    def __init__(self, message):
        super().__init__(message)


class TemplateNotFoundException(Exception):
    """
    Occurs when BYOM template is not found in the environment

    """
    def __init__(self, message):
        super().__init__(message)


class TrainConfigException(Exception):
    """
    Occurs when BYOM Train Config is not found in the environment

    """
    def __init__(self, message):
        super().__init__(message)


class RunConfigException(Exception):
    """
    Occurs when BYOM Run Config is not found in the environment

    """
    def __init__(self, message):
        super().__init__(message)
