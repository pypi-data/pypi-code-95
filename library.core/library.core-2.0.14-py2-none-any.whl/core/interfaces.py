# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.app.discussion.interfaces import IDiscussionLayer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ILibraryCoreLayer(IDefaultBrowserLayer, IDiscussionLayer):
    """Marker interface that defines a browser layer."""
