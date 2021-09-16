import typing

from django.conf import settings


__all__ = ['configurations']


class HealthConfiguration:
    @property
    def enabled(self) -> bool:
        """
        Health enabled flag
        """
        return getattr(settings, 'HEALTH_CHECKERS_ENABLED', True)

    @property
    def checkers(self) -> typing.Set[str]:
        """
        Health checkers (classes)
        """
        default_checkers = {
            'health.checkers.disk.DiskHealthChecker',
            'health.checkers.database.DatabaseHealthChecker',
            'health.checkers.cache.CacheHealthChecker'
        }
        return getattr(settings, 'HEALTH_CHECKERS', default_checkers)

    @property
    def context_path(self) -> str:
        """
        Health checkers context path
        """
        return getattr(settings, 'HEALTH_CHECKERS_CONTEXT_PATH', '/infra')


configurations = HealthConfiguration()
