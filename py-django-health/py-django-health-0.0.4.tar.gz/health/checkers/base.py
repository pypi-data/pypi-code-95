import typing

from health.models import ComponentHealth


class HealthChecker:
    def setup(self) -> typing.NoReturn:
        """
        Setup configurations before start.
        """
        pass

    def check(self) -> typing.List[ComponentHealth]:
        """
        Check component health.

        :return:
        """
        raise NotImplementedError()


class DisabledHealthChecker(HealthChecker):
    """
    Disabled health checker
    """
    def check(self) -> typing.List[ComponentHealth]:
        return []
