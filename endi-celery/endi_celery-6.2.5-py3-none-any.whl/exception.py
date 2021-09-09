# -*- coding: utf-8 -*-
"""
Custom exceptions
"""


class BaseException(Exception):
    def __init__(self, message=''):
        self.message = message


class MissingMandatoryArgument(BaseException):
    """
    Raised when a mandatory argument is missing
    """
    pass


class InstanceNotFound(BaseException):
    """
    Raised when no instance could be found
    """
    pass


class MultipleInstanceFound(BaseException):
    """
    Raised when no instance could be found
    """
    pass
