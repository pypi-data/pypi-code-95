import typing
import logging

from django.conf import settings
from django.core.cache import caches
from django.core.cache import CacheKeyWarning

from health.checkers.base import HealthChecker
from health.consts import Status
from health.models import ComponentHealth
from health.models import CacheHealth


log = logging.getLogger('health.checkers.cache')


class CacheHealthChecker(HealthChecker):
    _caches: dict
    _test_key: str
    _test_content: str

    def setup(self) -> typing.NoReturn:
        self._caches = getattr(settings, 'CACHES', {})
        self._test_key = 'health.checker.cache.test.key'
        self._test_content = 'HEALTHY'

    def check(self) -> typing.List[ComponentHealth]:
        components = []
        for alias in getattr(settings, 'CACHES', {}):
            cache = caches[alias]

            health = CacheHealth()
            health.name = alias
            health.backend = self._caches[alias]['BACKEND']

            try:
                cache.set(self._test_key, self._test_content)

                content = cache.get(self._test_key)
                if content != self._test_content:
                    raise AssertionError(f'Expected {self._test_content}, got: {content}')

                cache.delete(self._test_key)
                if cache.get(self._test_key):
                    raise CacheKeyWarning(f'Key {self._test_key} was deleted but it is still there!')

            except AssertionError as ex:
                log.error(f'CacheHealthChecker: {ex}')
                health.status = Status.UNKNOWN

            except CacheKeyWarning as ex:
                log.warning(f'CacheHealthChecker: {ex}')
                health.status = Status.UNKNOWN

            except Exception as ex:
                log.error(f'CacheHealthChecker: {ex}')
                health.status = Status.DEAD

            finally:
                components.append(health)

        return components
