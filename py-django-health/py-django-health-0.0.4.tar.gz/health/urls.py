from urllib.parse import urljoin

from django.urls import path

from health.api import resolve_health
from health.conf import configurations


def resolve_path(uri: str) -> str:
    """
    Resolves path by given uri.

    :param uri: uri
    :return: path with context path
    """
    return urljoin(configurations.context_path, uri)


urlpatterns = [
    path(resolve_path('health'), resolve_health)
]
