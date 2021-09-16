import typing
import logging

from django.conf import settings
from django.db import connections
from django.db import Error as DBError

from health.checkers.base import HealthChecker
from health.consts import Status
from health.models import ComponentHealth
from health.models import DatabaseHealth


log = logging.getLogger('health.checkers.database')


class DatabaseHealthChecker(HealthChecker):
    """
    Database health checker.

    Executes only one query (SELECT 1) to check if the database is alive.
    """
    _databases: dict

    def setup(self) -> typing.NoReturn:
        self._databases = getattr(settings, 'DATABASES', {})

    def _get_uri(self, alias: str, vendor: str) -> str:
        db_conf = self._databases[alias]

        if vendor in ['sqlite', 'unknown']:
            return db_conf.get('NAME', '!unknown')

        host = db_conf.get('HOST', '!unknown')
        port = db_conf.get('PORT', '!unknown')
        uri = f"{vendor}://{host}:{port}"

        database = db_conf.get('NAME')
        if database:
            uri += f'/{database}'

        return uri

    def check(self) -> typing.List[ComponentHealth]:
        components = []
        for alias in self._databases:
            connection = connections[alias]

            health = DatabaseHealth()
            health.name = alias
            health.vendor = connection.vendor
            health.uri = self._get_uri(connection.vendor, alias)

            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    one = cursor.fetchone()[0]
                    if one != 1:
                        raise AssertionError(f'Expected 1, got: {one}')

            except DBError as ex:
                log.error(f'DatabaseHealthChecker: {ex}')
                health.status = Status.DEAD

            except AssertionError as ex:
                log.warning(f'DatabaseHealthChecker: {ex}')
                health.status = Status.UNKNOWN

            finally:
                components.append(health)

        return components
