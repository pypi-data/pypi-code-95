import logging

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators import http

from health.service import checker
from health.service import get_status


__all__ = ['resolve_health']


log = logging.getLogger('health.api')


@http.require_GET
def resolve_health(request: HttpRequest) -> HttpResponse:
    """
    Endpoint to resolve health information.

    :param request: http request
    :returns: app health information and its components
    """
    log.info('Resolving health for application.')

    components = checker.check()

    return JsonResponse({
        "status": get_status(components),
        "components": [component.dict(exclude_unset=True) for component in components]
    }, status=200)
