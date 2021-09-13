"""Defines the exceptions for the package

.. moduleauthor: David "Gahd" Couples <gahdania@gahd.io>
"""

class BNetError(Exception):
    """Base Error class for BattleNet Client"""
    pass


class BNetRegionNotFoundError(BNetError):
    """Error raised when an invalid region code is detected"""
    pass


class BNetDataNotFoundError(BNetError):
    """Error raised when the Battle.net API returns a 404"""
    pass


class BNetAccessForbiddenError(BNetError):
    """Error raised with the Battle.net API returns a 403"""
    pass


class BNetClientError(BNetError):
    """Error raised if there is a mismatch with the client and API endpoints"""
    pass
