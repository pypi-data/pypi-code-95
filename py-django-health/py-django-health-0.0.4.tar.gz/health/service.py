import math
import typing
import importlib
import logging

from django.conf import ImproperlyConfigured

from health.consts import Status
from health.models import ComponentHealth
from health.checkers.base import HealthChecker


__all__ = ['checker', 'get_status']


log = logging.getLogger('health.service')


class _CheckerService:
    _checkers: typing.Dict[str, HealthChecker]

    def __init__(self):
        self._checkers = {}

    def register(self, checker_pkg: str) -> typing.NoReturn:
        """
        Register health checker instances.

        :param checker_pkg: checker_pkg
        """
        try:
            checker_module, checker_cls = checker_pkg.rsplit('.', 1)
            module = importlib.import_module(checker_module)
            cls = getattr(module, checker_cls)

            _checker = cls()
            if not isinstance(_checker, HealthChecker):
                raise ValueError(f"is not an instance of HealthChecker")
            _checker.setup()

            self._checkers[checker_pkg] = _checker

        except ModuleNotFoundError as ex:
            log.error(f'{checker_pkg} health checker: {ex}')
            raise ImproperlyConfigured('module not found')

        except AttributeError as ex:
            log.error(f'{checker_pkg} health checker: {ex}')
            raise ImproperlyConfigured('attribute error')

        except ValueError as ex:
            log.error(f'{checker_pkg} health checker: {ex}')
            raise ImproperlyConfigured('value error')

    def check(self) -> typing.List[ComponentHealth]:
        """
        Check all components

        :return: component health list
        """
        components = []
        for key, _checker in self._checkers.items():
            log.debug(f'Checking {key} health...')
            components += _checker.check()
        return components


def get_status(components: typing.List[ComponentHealth]) -> Status:
    """
    Calculates the over-all status by a given list of components health.

    :param components: list of health components
    :returns:
        Status.DEAD: if half or more than the half of the components have DEAD status
        Status.UNKNOWN: if half or more than the half of the components have UNKNOWN status
        Status.ALIVE: if more than the half of the components have ALIVE status
    """
    total = len(components)
    if total == 0:
        return Status.ALIVE

    components_alive = list(filter(lambda component: Status.ALIVE == component.status, components))
    components_dead = list(filter(lambda component: Status.DEAD == component.status, components))
    components_unknown = list(filter(lambda component: Status.UNKNOWN == component.status, components))

    half_total = math.floor(total/2.0)
    if len(components_dead) >= half_total:
        return Status.DEAD

    if len(components_unknown) >= half_total:
        return Status.UNKNOWN

    if len(components_alive) > half_total:
        return Status.ALIVE

    return Status.UNKNOWN


checker = _CheckerService()
