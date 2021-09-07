# -*- coding: utf-8 -*-
"""
    pip_services_common.refer.ReferenceException
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Reference error type
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, Optional

from ..errors.InternalException import InternalException


class ReferenceException(InternalException):
    """
    Error when __required component dependency cannot be found.
    """

    def __init__(self, correlation_id: Optional[str] = None, locator: Any = None):
        """
        Creates an error instance and assigns its values.

        :param correlation_id: (optional) a unique transaction id to trace execution through call chain.

        :param locator: the locator to find reference to dependent component.
        """
        message = 'Cannot locate reference: ' + (str(locator) if not (locator is None) else '<None>')
        super(ReferenceException, self).__init__(correlation_id, "REF_ERROR", message)
        self.with_details('locator', locator)
