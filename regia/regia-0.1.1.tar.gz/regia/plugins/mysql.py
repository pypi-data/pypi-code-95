from django.db import DEFAULT_DB_ALIAS
from django.db import connections

from ._db import ensure_databases


@ensure_databases
def connection(use=DEFAULT_DB_ALIAS):
    return connections[use]
