#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.request module


"""

import logging

from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy, IRequest, \
    IRequestFactory
from pyramid.request import Request
from pyramid.security import Allowed
from pyramid.threadlocal import get_current_registry, get_current_request
from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.interface import Interface, alsoProvides

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces import DISPLAY_CONTEXT_KEY_NAME, ICacheKeyValue, MissingRequestError
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (utils)')

_MARKER = object()


class RequestSelector:
    """Interface based request selector

    This selector can be used as a subscriber predicate to define
    an interface that the event's 'request' attribute must support for the event to be applied:

    .. code-block:: python

        from pyams_utils.interfaces.site import ISiteRoot

        @subscriber(IBeforeTraverseEvent, request_selector=IPyAMSLayer)
        def before_traverse_event(event):
            '''This is an event handler for an IPyAMSRequest modification event'''
    """

    def __init__(self, ifaces, config):  # pylint: disable=unused-argument
        if not isinstance(ifaces, (list, tuple, set)):
            ifaces = (ifaces,)
        self.interfaces = ifaces

    def text(self):
        """Predicate label"""
        return 'request_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event):
        for intf in self.interfaces:
            try:
                if intf.providedBy(event.request):
                    return True
            except (AttributeError, TypeError):
                if isinstance(event.request, intf):
                    return True
        return False


def request_property(key=None, prefix=None):
    """Define a method decorator used to store result into current request's annotations

    If no request is currently running, a new one is created.
    `key` is a required argument; if None, the key will be the method's object

    :param str|func key: annotations value key; if *None*, the key will be the method's object; if
        *key* is a callable object, it will be called to get the actual session key
    :param str prefix: prefix to use for session key; if *None*, the prefix will be the property
        name
    """

    def request_decorator(func):

        def wrapper(obj, key, *args, **kwargs):
            request = query_request()
            if request is not None:
                if callable(key):
                    key = key(obj, request, *args, **kwargs)
                if not key:
                    key = prefix or func.__name__
                    if obj is not request:
                        key += '::{0}'.format(ICacheKeyValue(obj))
                    key_args = tuple(filter(lambda x: x is not request, args))
                    if key_args:
                        key += '::' + '::'.join((ICacheKeyValue(arg) for arg in key_args))
                    if kwargs:
                        key += '::' + \
                               '::'.join(('{0}={1}'.format(key, ICacheKeyValue(val))
                                          for key, val in kwargs.items()))
                LOGGER.debug(">>> Looking for request cache key {0}".format(key))
                data = get_request_data(request, key, _MARKER)
                if data is _MARKER:
                    LOGGER.debug("<<< no cached value!")
                    data = func
                    if callable(data):
                        data = data(obj, *args, **kwargs)
                    set_request_data(request, key, data)
                else:
                    LOGGER.debug("<<< cached value found!")
                    LOGGER.debug("  < {0!r}".format(data))
            else:
                data = func
                if callable(data):
                    data = data(obj, *args, **kwargs)
            return data

        return lambda x, *args, **kwargs: wrapper(x, key, *args, **kwargs)

    return request_decorator


class PyAMSRequest(Request):
    """Custom request factory

    Used to add 'context' argument to 'effective_principals' method call
    to be able to get 'roles' principals
    """

    @request_property(key=None)
    def has_permission(self, permission, context=None):
        if context is None:
            context = self.context  # pylint: disable=no-member
        try:
            reg = self.registry
        except AttributeError:
            reg = get_current_registry()
        authn_policy = reg.queryUtility(IAuthenticationPolicy)
        if authn_policy is None:
            return Allowed('No authentication policy in use.')
        authz_policy = reg.queryUtility(IAuthorizationPolicy)
        if authz_policy is None:
            raise ValueError('Authentication policy registered without '
                             'authorization policy')  # should never happen
        try:
            principals = authn_policy.effective_principals(self, context=context)
        except TypeError:
            principals = authn_policy.effective_principals(self)
        return authz_policy.permits(context, principals, permission)


def get_request(raise_exception=True):
    """Get current request

    Raises a NoInteraction exception if there is no active request.
    """
    request = get_current_request()
    if (request is None) and raise_exception:
        raise MissingRequestError("No request")
    return request


def query_request():
    """Query current request

    Returns None if there is no active request"""
    try:
        return get_request()
    except MissingRequestError:
        return None


# pylint: disable=invalid-name,too-many-arguments,attribute-defined-outside-init
def check_request(path='/', environ=None, base_url=None, headers=None,
                  POST=None, registry=None, principal_id=None, **kwargs):
    """Get current request, or create a new blank one if missing"""
    try:
        return get_request()
    except MissingRequestError:
        if registry is None:
            registry = get_current_registry()
        factory = registry.queryUtility(IRequestFactory)
        if factory is None:
            factory = PyAMSRequest
        request = factory.blank(path, environ, base_url, headers, POST, **kwargs)
        request.registry = registry  # pylint: disable=attribute-defined-outside-init
        request.context = kwargs.get('context', None)
        if principal_id is not None:
            try:
                # pylint: disable=import-outside-toplevel
                from pyams_security.utility import get_principal
            except ImportError:
                pass
            else:
                request.principal = get_principal(request, principal_id)
        return request


def copy_request(request):
    """Create clone of given request, keeping registry and root as well"""
    root = getattr(request, 'root', None)
    request = request.copy()
    if not hasattr(request, 'registry'):
        registry = get_current_registry()
        request.registry = registry
    request.root = root
    return request


def get_annotations(request):
    """Define 'annotations' request property

    This function is automatically defined as a custom request method on package include.
    """
    alsoProvides(request, IAttributeAnnotatable)
    return IAnnotations(request)


def get_debug(request):  # pylint: disable=unused-argument
    """Define 'debug' request property

    This function is automatically defined as a custom request method on package include.
    """
    class Debug():
        """Request debug class"""
        def __init__(self):
            self.showTAL = False
            self.sourceAnnotations = False
    return Debug()


def get_request_data(request, key, default=None):
    """Get data associated with request

    :param request: the request containing requested data
    :param str key: request data annotation key
    :param object default: the default value when data is missing
    :return: the requested value, or *default*
    """
    try:
        annotations = request.annotations
    except (TypeError, AttributeError):
        annotations = get_annotations(request)
    return annotations.get(key, default)


def set_request_data(request, key, value):
    """Associate data with request

    :param request: the request in which to set data
    :param str key: request data annotation key
    :param object value: the value to be set in request annotation
    """
    try:
        annotations = request.annotations
    except (TypeError, AttributeError):
        annotations = get_annotations(request)
    annotations[key] = value


def get_display_context(request):
    """Get current display context

    The display context can be used when we generate a page to display an object in the context
    of another one; PyAMS_content package is using this feature to display "shared" contents as
    is they were located inside another site or folder...
    """
    return get_request_data(request, DISPLAY_CONTEXT_KEY_NAME, request.context)


@adapter_config(name='request_data',
                required=(Interface, IRequest, Interface),
                provides=ITALESExtension)
class RequestDataExtension(ContextRequestViewAdapter):
    """extension:request_data TALES extension for Pyramid request

    This TALES extension can be used to get a request data, previously stored in the request via
    an annotation.

    For example:

    .. code-block:: xml

        <div tal:content="extension:request_data('my.annotation.key')">...</div>
    """

    def render(self, key, default=None):
        """See :py:class:`ITALESExtension <pyams_utils.interfaces.tales.ITALESExtension>`
        interface
        """
        return get_request_data(self.request, key, default)
