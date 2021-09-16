import os
import shutil
import typing
import logging

from health.checkers.base import HealthChecker
from health.consts import Status
from health.models import ComponentHealth
from health.models import DiskHealth


log = logging.getLogger('health.checkers.disk')


class DiskHealthChecker(HealthChecker):
    _test_file_path: str
    _test_file_content: str

    def setup(self) -> typing.NoReturn:
        self._test_file_path = os.path.expanduser('~/disk_health_test.txt')
        self._test_file_content = 'HEALTHY'

    def check(self) -> typing.List[ComponentHealth]:
        health = DiskHealth()

        try:
            test = open(self._test_file_path, 'w')
            test.write(self._test_file_content)
            test.close()

            if not os.path.isfile(self._test_file_path):
                raise IOError(f'{self._test_file_path} is not a file')

            test = open(self._test_file_path, 'r')
            content = test.read()
            test.close()

            if self._test_file_content != content:
                raise AssertionError(f'Expected {self._test_file_content}, got: {content}')

            os.remove(self._test_file_path)
            if os.path.isfile(self._test_file_path):
                raise IOError(f'{self._test_file_path} was not removed')

            disk = shutil.disk_usage("/")

            health.total = disk.total
            health.free = disk.free
            health.used = disk.used

        except OSError as ex:
            log.error(f"DiskHealthChecker: {ex}")
            health.status = Status.DEAD

        except AssertionError as ex:
            log.warning(f"DiskHealthChecker: {ex}")
            health.status = Status.UNKNOWN

        finally:
            return [health]
