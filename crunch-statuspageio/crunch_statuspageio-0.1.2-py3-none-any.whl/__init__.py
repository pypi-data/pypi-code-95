"""
StatusPage.io  API V1 library client for Python.
~~~~~~~~~~~~~~~~~~~~~
Usage::
  >>> import statuspageio
  >>> client = statuspageio.Client(api_key=os.environ.get('STATUSPAGE_API_KEY')
  >>> status = client.components.list()
  >>> print status
:copyright: (c) 2016 by GameSparks TechOps (techops@gamesparks.com).
:license: MIT, see LICENSE for more details.
"""

from statuspageio.errors import (
    ConfigurationError,
    RateLimitError,
    BaseError,
    RequestError,
    ResourceError,
    ServerError
)

from statuspageio.configuration import Configuration
from statuspageio.http_client import HttpClient

from statuspageio.services import (
    PageService,
    ComponentsService,
    IncidentsService,
    SubscribersService,
    MetricsService,
    UsersService,
)

from statuspageio.client import Client

__all__ = [
    'ConfigurationError',
    'RateLimitError',
    'BaseError',
    'RequestError',
    'ResourceError',
    'ServerError',
    'Configuration',
    'HttpClient',
    'PageService',
    'ComponentsService',
    'IncidentsService',
    'SubscribersService',
    'MetricsService',
    'UsersService',
    'Client',
]
