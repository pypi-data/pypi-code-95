# -*- coding: utf-8 -*-
"""
    pip_services3_commons.errors.ErrorCategory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Error categories enumeration
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

class ErrorCategory(object):
    """
    Defines standard error categories to application exceptions supported by PipServices toolkit.
    """

    Unknown: str = 'Unknown'
    """
    Unknown or unexpected errors
    """

    Internal: str = 'Internal'
    """
    Internal errors caused by programming mistakes
    """

    Misconfiguration: str = 'Misconfiguration'
    """
    Errors related to mistakes in user-defined configuration
    """

    InvalidState: str = 'InvalidState'
    """
    Errors related to operations called in wrong component state.
    For instance, business calls when component is not ready
    """

    NoResponse: str = 'NoResponse'
    """
    Errors happened during connection to remote services.
    They can be related to misconfiguration, network issues
    or remote service itself 
    """

    FailedInvocation: str = 'FailedInvocation'
    """
    Errors returned by remote services or network
    during call attempts
    """

    FileError: str = 'FileError'
    """
    Errors in read/write file operations
    """

    BadRequest: str = 'BadRequest'
    """
    Errors due to improper user requests, like
    missing or wrong parameters 
    """

    Unauthorized: str = 'Unauthorized'
    """
    Access errors caused by missing user identity
    or security permissions
    """

    NotFound: str = 'NotFound'
    """
    Error caused by attempt to access missing object
    """

    Conflict: str = 'Conflict'
    """
    Errors raised by conflict in object versions
    posted by user and stored on server.
    """

    Unsupported: str = 'Unsupported'
    """
    Errors caused by calls to unsupported
    or not yet implemented functionality
    """
