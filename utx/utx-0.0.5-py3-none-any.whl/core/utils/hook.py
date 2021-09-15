#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  9/14/2021 3:36 PM
@Desc    :  Hook line.
"""
import logging
import allure
import pytest

from logging import getLogger
from airtest.core.api import *
from airtest.core.helper import device_platform, ST
from tenacity import Retrying, wait_fixed, stop_after_attempt
from wda import WDAError
from utx.core.utils.tools import str_to_bool

logger = getLogger(__name__)


def app_info(cli_platform, cli_device, cli_wda, cli_init, ini_platform, ini_device, ini_wda, ini_init):
    """

    :param cli_platform:
    :param cli_device:
    :param cli_wda:
    :param cli_init:
    :param ini_platform:
    :param ini_device:
    :param ini_wda:
    :param ini_init:
    :return:
    """
    if cli_init is None:
        is_init = str_to_bool(ini_init)
    else:
        is_init = str_to_bool(cli_init)

    if cli_platform is None:
        platform = ini_platform.lower()
        if platform in 'android':
            device_idx = ini_device
            device_uri = 'Android:///{}?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=MAXTOUCH'.format(device_idx)
            return device_uri, device_idx, is_init
        elif platform in 'ios':
            device_idx = ini_device
            device_uri = 'iOS:///{}'.format(device_idx)
            return device_uri, device_idx, is_init

    elif cli_platform is not None:
        if cli_platform.lower() in 'android':
            device_idx = cli_device
            device_uri = 'Android:///{}?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=MAXTOUCH'.format(device_idx)
            return device_uri, device_idx, is_init
        elif cli_platform.lower() in 'ios':
            device_idx = cli_device
            device_uri = 'iOS:///{}'.format(device_idx)
            return device_uri, device_idx, is_init


def my_before_sleep(retry_state):
    """

    :param retry_state:
    :return:
    """
    if retry_state.attempt_number < 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING

    logging.log(
        loglevel,
        'Retrying %s: attempt %s ended with: %s',
        retry_state.fn,
        retry_state.attempt_number,
        retry_state.outcome,
    )


@allure.step("Try to link the device！")
def my_retry_connect(uri=None, whether_retry=True, sleeps=10, max_attempts=3):
    """

    :param uri:
    :param whether_retry:
    :param sleeps:
    :param max_attempts:
    :return:
    """
    if not whether_retry:
        max_attempts = 1

    r = Retrying(wait=wait_fixed(sleeps), stop=stop_after_attempt(max_attempts), before_sleep=my_before_sleep,
                 reraise=True)
    try:
        return r(connect_device, uri)
    except Exception as e:
        if isinstance(e, (WDAError,)):
            logger.info("Can't connect iphone, please check device or wda state!")
        logger.info("Try connect device {} 3 times per wait 10 sec failed.".format(uri))
        raise e
    finally:
        logger.info("Retry connect statistics: {}".format(str(r.statistics)))


@allure.step("Switch to current device！")
def ensure_current_device(device_idx):
    """

    :param device_idx:
    :return:
    """
    idx = device_idx
    if device().uuid != idx:
        set_current(idx)


@allure.step("Try to wake up the current device！")
def wake_device(current_device):
    """

    :param current_device:
    :return:
    """
    current_device.wake()


def app_fixture(request, device_uri, app_filepath, app_name, device_idx, init):
    """

    :param request:
    :param device_uri:
    :param app_filepath:
    :param app_name:
    :param device_idx:
    :param init:
    :return:
    """
    with allure.step("Initialize and generate APP object！"):
        logger.info("Session start test.")
        ST.THRESHOLD = 0.7
        ST.OPDELAY = 0.25
        ST.FIND_TIMEOUT = 10
        ST.FIND_TIMEOUT_TMP = 2
        ST.SNAPSHOT_QUALITY = 10

        try:
            app = None

            app = my_retry_connect(device_uri)
            if init:
                install(app_filepath)
            else:
                pass

        except Exception as e:
            logger.error("Create app fail: {}".format(e))
            allure.attach(body='',
                          name="Create app fail: {}".format(e),
                          attachment_type=allure.attachment_type.TEXT)
            pytest.exit("Create app fail: {}".format(e))

        assert (app is not None)

        ensure_current_device(device_idx)

        logger.info("Current test platform: {}".format(device_platform()))
        logger.info("start app {0} in {1}:{2}".format(app_name, device_platform(), G.DEVICE.uuid))

        wake_device(G.DEVICE)

    def teardown_test():
        with allure.step("Teardown session"):
            stop_app(app_name)
            if init:
                uninstall(app_name)
            else:
                pass

        logger.info("Session stop test.")

    request.addfinalizer(teardown_test)

    return app
