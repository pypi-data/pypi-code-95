# -*- coding: utf-8 -*-
"""
    pip_services3_commons.errors.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Portable and localizable Exceptions classes. Each Exception, in addition to a description
    and stack trace has a unique string code, details array (which can be used for creating localized strings).

    Way to use:
    - An existing error class can be used.
    - A child class that extends ApplicationException can we written.
    - A error can be wrapped around (into?) an existing application error.

    Exceptions are serializable. The error classes themselves are not serializable, but
    they can be converted to ErrorDescriptions, which are serializable in one language, transferred
    to the receiving side, and deserialized in another language. After deserialization, the initial
    error class can be restored.

    Additionally: when transferring an error from one language to another, the error type
    that is closest to the initial error type is chosen from the exceptions available in the target language.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'ErrorCategory', 'ErrorDescription', 'ApplicationException',
    'ApplicationExceptionFactory', 'ErrorDescriptionFactory',
    'UnknownException', 'InternalException', 'ConfigException',
    'InvalidStateException', 'ConnectionException', 'InvocationException',
    'FileException', 'BadRequestException', 'NotFoundException', 
    'UnauthorizedException', 'ConflictException', 'UnsupportedException'
]

from .ErrorCategory import ErrorCategory
from .ErrorDescription import ErrorDescription
from .ApplicationException import ApplicationException
from .ApplicationExceptionFactory import ApplicationExceptionFactory
from .ErrorDescriptionFactory import ErrorDescriptionFactory
from .UnknownException import UnknownException
from .InternalException import InternalException
from .ConfigException import ConfigException
from .InvalidStateException import InvalidStateException
from .ConnectionException import ConnectionException
from .InvocationException import InvocationException
from .FileException import FileException
from .BadRequestException import BadRequestException
from .NotFoundException import NotFoundException
from .UnauthorizedException import UnauthorizedException
from .ConflictException import ConflictException
from .UnsupportedException import UnsupportedException