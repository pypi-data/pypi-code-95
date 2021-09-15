#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from json import loads

from django.http import QueryDict, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, resolve_url
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from djangokit.views import controller

from textrank import __version__
from textrank.conf import LOGIN_URL, LOGOUT_URL, DEMO_MODE
from textrank.decorators import user_access_required, api_access_required


def get_default_context():
    ctx = {
        'VERSION': __version__,
        'LOGIN_URL': resolve_url(LOGIN_URL),
        'LOGOUT_URL': resolve_url(LOGOUT_URL),
        'DEMO_MODE': DEMO_MODE,
    }
    return ctx


def parse_params(request):
    if request.content_type == 'application/json':
        return loads(request.body.decode('utf-8'))
    method = request.method
    if method == 'GET':
        return request.GET
    elif method == 'POST':
        return request.POST
    return QueryDict(request.body)


@method_decorator(user_access_required, name='dispatch')
class UserAccessMixin:
    """Mixing for user access."""

    def dispatch(self, request, *args, **kwargs):
        if DEMO_MODE and request.method != 'GET':
            # В демо-режиме не позволяем анонимам изменять данные.
            if not request.user.is_authenticated:
                return HttpResponseForbidden(_(
                    'Авторизируйтесь, чтобы иметь возможность редактировать '
                    'данные.'
                ))
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(api_access_required, name='dispatch')
class ApiAccessMixin:
    """Mixing for API access."""
    def dispatch(self, *args, **kwargs):
        return super(ApiAccessMixin, self).dispatch(*args, **kwargs)


class BaseModelView(controller.ControlModelView):

    def get_default_context(self, *args, **kwargs):
        return get_default_context()

    def delete(self, request, id=None):
        if id:
            instance = get_object_or_404(self.model, id=id)
            instance.delete()
        else:
            self.model.objects.all().delete()
        return JsonResponse({'success': True, 'id': id})
