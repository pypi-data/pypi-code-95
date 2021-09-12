# -*- coding: utf-8 -*-
"""
    pip_services_common.errors.UnauthorizedException
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Unauthorized error type
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from .ApplicationException import ApplicationException
from .ErrorCategory import ErrorCategory


class UnauthorizedException(ApplicationException):
    """
    Access errors caused by missing user identity (authentication error)
    or incorrect security permissions (authorization error).
    """

    def __init__(self, correlation_id: Optional[str] = None, code: str = None, message: str = None):
        """
        Creates an error instance and assigns its values.

        :param correlation_id: (optional) a unique transaction id to trace execution through call chain.

        :param code: (optional) a unique error code. Default: "UNKNOWN"

        :param message: (optional) a human-readable description of the error.
        """
        super(UnauthorizedException, self).__init__(ErrorCategory.Unauthorized, correlation_id, code, message)
        self.status = 401
