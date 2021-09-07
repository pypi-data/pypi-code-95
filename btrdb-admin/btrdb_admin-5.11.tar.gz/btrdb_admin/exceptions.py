# btrdb_admin.exceptions
# Module for custom exceptions
#
# Author:   PingThings
# Created:  Wed Mar 27 12:42:26 2019 -0400
#
# For license information, see LICENSE.txt
# ID: exceptions.py [] allen@pingthings.io $

"""
Module for custom exceptions
"""


class BTRDBError(Exception):
    pass


class ConnectionError(BTRDBError):
    """
    An error occurred trying to establish a connection to the API
    """
    pass


class CredentialsFileNotFound(FileNotFoundError):
    """
    The credentials file could not be found.
    """
    pass


class ProfileNotFound(BTRDBError):
    """
    A requested profile could not be found in the credentials file.
    """
    pass


class AdminAPIError(BTRDBError):

    @classmethod
    def from_response(klass, error):
        if not hasattr(error, "code") or not hasattr(error, "msg"):
            if hasattr(error, "error"):
                return klass.from_response(error.error)
            else:
                raise TypeError("response does not contain an error")

        if error.code == 0:
            return None
        return klass(error.code, error.msg)

    @classmethod
    def check_error(klass, error):
        e = klass.from_response(error)
        if e is not None:
            raise e

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return "<{} [{}] {}>".format(
            self.__class__.__name__, self.code, self.message
        )

    def __str__(self):
        return "[{}] {}".format(self.code, self.message)


class NotFoundError(AdminAPIError):
    """
    An error has occurred while attempting to retrieve an item that does not exist
    """
    pass
