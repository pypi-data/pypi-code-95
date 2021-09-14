"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEeaDexterityIndicatorsLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IIndicator(Interface):
    """ Marker interface for IMS Indicator
    """
