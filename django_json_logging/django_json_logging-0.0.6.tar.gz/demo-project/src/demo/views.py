import logging

from django.http import HttpRequest, HttpResponse

log = logging.getLogger(__name__)


def info(request: HttpRequest) -> HttpResponse:
    log.info("getting some info ...")
    return HttpResponse("some response")
