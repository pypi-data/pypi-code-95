# -*- coding: utf-8 -*-
"""
    pip_services3_commons.errors.ApplicationException
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Application error type
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import traceback
from typing import Optional, Any

from pip_services3_commons.data import StringValueMap
from .ErrorCategory import ErrorCategory


class ApplicationException(Exception):
    """
    Defines a base class to defive various application exceptions.

    Most languages have own definition of base error (error) types.
    However, this class is implemented symmetrically in all languages
    supported by PipServices toolkit. It allows to create portable implementations
    and support proper error propagation in microservices calls.

    Error propagation means that when microservice implemented in one language
    calls microservice(s) implemented in a different language(s), errors are returned
    throught the entire call chain and restored in their original (or close) type.

    Since number of potential error types is endless, PipServices toolkit
    supports only 12 standard categories of exceptions defined in :class:`ErrorCategory`.
    This :class:`ApplicationException <pip_services3_commons.errors.ApplicationException.ApplicationException>` class acts as a basis for all obj 12 standard error types.

    Most exceptions have just free-form message that describes occured error.
    That may not be sufficient to create meaninful error descriptions.
    The :class:`ApplicationException <pip_services3_commons.errors.ApplicationException.ApplicationException>` class proposes an extended error definition that has more standard fields:
    - message: is a human-readable error description
    - category: one of 12 standard error categories of errors
    - status: numeric HTTP status code for REST invocations
    - code: a unique error code, usually defined as "MY_ERROR_CODE"
    - correlation_id: a unique transaction id to trace execution through a call chain
    - details: map with error parameters that can help to recreate meaningful error description in obj languages
    - stack_trace: a stack trace
    - cause: original error that is wrapped by this error

    ApplicationException class is not serializable. To pass errors through the wire
    it is converted into :class:`ErrorDescription <pip_services3_commons.errors.ErrorDescription.ErrorDescription>` <pip_services3_commons.errors.ErrorDescription.ErrorDescription>` object and restored on receiving end into identical error type.
    """

    def __init__(self, category: str = ErrorCategory.Unknown, correlation_id: Optional[str] = None,
                 code: str = 'UNKNOWN', message: str = 'Unknown error'):
        """
        Creates a new instance of application error and assigns its values.

        :param category: (optional) a standard error category. Default: Unknown

        :param correlation_id: (optional) a unique transaction id to trace execution through call chain.

        :param code: (optional) a unique error code. Default: "UNKNOWN"

        :param message: (optional) a human-readable description of the error.
        """
        super(ApplicationException, self).__init__(message)

        # A human-readable error description (usually written in English)
        self.message: str = message
        # Standard error category
        self.category: str = category or ErrorCategory.Unknown
        # HTTP status code associated with this error type
        self.status: int = 500
        # A unique error code
        self.code: str = code or 'UNKNOWN'
        # A map with additional details that can be used to restore error description in obj languages
        self.details: StringValueMap = None
        # A unique transaction id to trace execution throug call chain
        self.correlation_id: Optional[str] = correlation_id
        # Stack trace of the error
        self.stack_trace: str = traceback.format_exc()
        #  Original error wrapped by this error
        self.cause: str = None
        self.name = code

    def __str__(self):
        return str(self.message) if not (self.message is None) else 'Unknown error'

    def to_json(self):
        return {
            'category': self.category,
            'code': self.code,
            'status': self.status,
            'details': self.details,
            'correlation_id': self.correlation_id,
            'message': self.message,
            'cause': str(self.cause),
            'stack_stace': self.stack_trace
        }

    def get_cause_string(self) -> str:
        """
        Gets original error wrapped by this error as a string message.

        :return: an original error message.
        """
        return str(self.cause)

    def set_cause_string(self, value: str):
        """
        Sets original error wrapped by this error as a string message.

        :param value: an original error message.
        """
        self.cause = value

    def get_stack_trace_string(self) -> Optional[str]:
        """
        Gets a stack trace where this error occured.

        :return: a stack trace as a string.
        """
        if not (self.stack_trace is None):
            return self.stack_trace
        # elif (hasattr(self, 'tb_frame')):
        #     return traceback.format_tb(self)
        else:
            return None

    def set_stack_trace_string(self, value: str):
        """
        Sets a stack trace where this error occured.

        :param value: a stack trace as a string
        """
        self.stack_trace = value

    def with_code(self, code: str) -> 'ApplicationException':
        """
        Sets a unique error code.
        This method returns reference to this error to implement Builder pattern to chain additional calls.

        :param code: a unique error code

        :return: this error object
        """
        self.code = code if code != None else 'UNKNOWN'
        self.name = code
        return self

    def with_status(self, status: int) -> 'ApplicationException':
        """
        Sets a HTTP status code which shall be returned by REST calls.
        This method returns reference to this error to implement Builder pattern to chain additional calls.

        :param status: an HTTP error code.

        :return: this error object
        """
        self.status = status if status != None else 500
        return self

    def with_details(self, key: str, value: Any) -> 'ApplicationException':
        """
        Sets a parameter for additional error details.
        This details can be used to restore error description in obj languages.

        This method returns reference to this error to implement Builder pattern to chain additional calls.

        :param key: a details parameter name

        :param value: a details parameter name

        :return: this error object
        """
        from ..data.StringValueMap import StringValueMap  # hack the circular import

        self.details = self.details or StringValueMap()
        self.details.set_as_object(key, value)
        return self

    def with_cause(self, cause: Exception) -> 'ApplicationException':
        """
        Sets a original error wrapped by this error

        This method returns reference to this error to implement Builder pattern to chain additional calls.

        :param cause: original error object

        :return: this error object
        """
        self.cause = cause
        return self

    def with_correlation_id(self, correlation_id: Optional[str]) -> 'ApplicationException':
        """
        Sets a correlation id which can be used to trace this error through a call chain.

        This method returns reference to this error to implement Builder pattern to chain additional calls.

        :param correlation_id: a unique transaction id to trace error through call chain

        :return: this error object
        """
        self.correlation_id = correlation_id
        return self

    def wrap(self, cause: Any) -> 'ApplicationException':
        """
        Wraps another error into an application error object.

        If original error is of ApplicationException type it is returned without changes.
        Otherwise a new ApplicationException is created and original error is set as its cause.

        :param cause: an original error object

        :return: an original or newly created ApplicationException
        """
        if isinstance(cause, ApplicationException):
            return cause

        self.with_cause(cause)
        return self

    @staticmethod
    def wrap_error(error: 'ApplicationException', cause: Any) -> 'ApplicationException':
        """
        Wraps another exception into specified application exception object.

        If original exception is of ApplicationException type it is returned without changes.
        Otherwise the original error is set as a cause to specified ApplicationException object.

        :param error: an ApplicationException object to wrap the cause

        :param cause: an original error object

        :return: an original or newly created ApplicationException
        """
        if isinstance(cause, ApplicationException):
            return cause

        error.with_cause(cause)
        return error

    def with_stack_trace(self, stack_trace: str) -> 'ApplicationException':
        """
        Sets a stack trace for this error.

        This method returns reference to this error to implement Builder pattern
        to chain additional calls.

        :param stack_trace: a stack trace where this error occured
        :return: this error object
        """
        self.stack_trace = stack_trace
        return self

    # @staticmethod
    # def from_value(args):
    #     args = args if isinstance(args, dict) else dict(args)
    #
    #     error = MicroserviceError(
    #         args['category'] if 'category' in args else None,
    #         args['correlation_id'] if 'correlation_id' in args else None,
    #         args['code'] if 'code' in args else None,
    #         args['message'] if 'message' in args else None
    #     ).with_status(args['status'])
    #
    #     if 'cause' in args:
    #         error.with_cause(args['cause'])
    #     if 'details' in args:
    #         error.with_details(args['details'])
    #     if 'stack_trace' in args:
    #         error.with_stack(args['stack_trace'])
    #
    #     return error
