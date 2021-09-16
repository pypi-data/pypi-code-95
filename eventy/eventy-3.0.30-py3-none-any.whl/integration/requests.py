# Copyright (c) Qotto, 2021

"""
Requests integration utilities

Utility functions to integrate the eventy protocol in apps using requests.

Usage::

    import eventy.integration.requests
    eventy.integration.requests.get('https://httpbin.org/get')
"""

import requests.api as vendor_requests_api
import requests.models as vendor_requests_models
import requests.sessions as vendor_requests_sessions

from eventy.trace_id import correlation_id_var

__all__ = [
    'Session',
    'session',
    'request',
    'get',
    'options',
    'head',
    'post',
    'put',
    'patch',
    'delete',
]


def _merge_docs(eventy_object, vendor_object) -> None:
    eventy_doc: str = getattr(eventy_object, '__doc__', '')
    vendor_doc: str = getattr(vendor_object, '__doc__', '')
    if vendor_doc:
        vendor_doc = f'\nVENDOR DOC:\n\n{vendor_doc}'
    merged_doc = eventy_doc + vendor_doc
    setattr(eventy_object, '__doc__', merged_doc)


class Session(vendor_requests_sessions.Session):
    """
    Modified implementation of vendor requests Session, propagating correlation_id.

    This class override ``prepare_request`` in order to insert x-correlation-id header.
    """

    def prepare_request(
        self,
        request: vendor_requests_models.Request
    ) -> vendor_requests_models.PreparedRequest:
        """
        Insert x-correlation-id header before calling vendor requests method.
        """
        if not request.headers:
            request.headers = {}
        request.headers.update({'x-correlation-id': correlation_id_var.get()})
        return super().prepare_request(request)


def session() -> Session:
    """
    Create a modified version of vendor Session, propagating correlation id.

    This function instantiates and returns a Session instance.
    """
    return Session()


def request(method, url, **kwargs):
    """
    Send a request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified Session class here
    with Session() as session:
        return session.request(method=method, url=url, **kwargs)


def get(url, params=None, **kwargs):
    """
    Send a GET request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('get', url, params=params, **kwargs)


def options(url, **kwargs):
    """
    Send a OPTIONS request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('options', url, **kwargs)


def head(url, **kwargs):
    """
    Send a HEAD request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    """
    Send a POST request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('post', url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    """
    Send a PUT request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    """
    Send a PATCH request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    """
    Send a DELETE request propagating correlation id.

    Keywords arguments are propagated to vendor implementation.
    """
    # Code is directly from vendor requests, using our modified request function here
    return request('delete', url, **kwargs)


_merge_docs(Session, vendor_requests_sessions.Session)
_merge_docs(session, vendor_requests_sessions.session)
_merge_docs(request, vendor_requests_api.request)
_merge_docs(get, vendor_requests_api.get)
_merge_docs(options, vendor_requests_api.options)
_merge_docs(head, vendor_requests_api.head)
_merge_docs(post, vendor_requests_api.post)
_merge_docs(put, vendor_requests_api.put)
_merge_docs(patch, vendor_requests_api.patch)
_merge_docs(delete, vendor_requests_api.delete)
