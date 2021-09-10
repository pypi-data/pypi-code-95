from pymongo import MongoClient

from django.conf import settings

from regia.exceptions import ConfigException
from ._db import ensure_databases

clients = {}


@ensure_databases
def connection(use: str):
    try:
        return clients[use]
    except KeyError:
        databases = getattr(settings, "DATABASES")
        kwargs = databases.get(use)
        if kwargs is None:
            raise ConfigException('could not find %s database configuration from `DATABASES`' % use)
        clients[use] = MongoClient(**kwargs)
    return clients[use]
