#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from textrank.conf import LOGIN_URL
from textrank.access import api_access, user_access


def user_access_required(function=None, login_url=LOGIN_URL,
                         raise_exception=False):
    """
    Decorator for views that checks whether a user access.
    """
    def check_perms(user):
        # First, check if the user has permission.
        if user_access(user):
            return True
        # If you need a 403 handler, throw an exception.
        if raise_exception:
            raise PermissionDenied
        # Or show the entry form.
        return False
    actual_decorator = user_passes_test(check_perms, login_url=login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


def api_access_required(function=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not (user_access(request.user) or api_access(request)):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator
