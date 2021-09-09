import pytest
import logging
from caterpillar_common.common.log import Log


@pytest.fixture(scope="session", autouse=True)
def init_testcase_log():
    log = Log(name="auto_test")
