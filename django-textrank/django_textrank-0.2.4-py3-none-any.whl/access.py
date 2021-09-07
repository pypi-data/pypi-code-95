#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Functions for access control.
"""
from djangokit.access.functions import levels
from textrank.conf import API_COOKIE_NAME, API_KEYS, ACCESS_LEVEL

# Автоматически выбранная по настройке settings.USER_ACCESS_LEVEL функция.
user_access = levels[ACCESS_LEVEL]


def api_access(request):
    """Checks the request for API."""
    key = request.COOKIES.get(API_COOKIE_NAME, '')
    if key in API_KEYS:
        request.META['API_KEY'] = key
        return True
    if 'API_KEY' in request.META:
        request.META.pop('API_KEY')
    return False
