#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/27
from typing import List
from contextlib import contextmanager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from easy_automation.utils.custom_logging import Logs
from easy_automation.contrib.after_error_hook import after_error_hook

log = Logs(__name__)


class SeleniumMixin:
    EXPLICIT_WAIT = 8

    @after_error_hook
    def find(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        """
        :param timeout:
        :param element_selector:
        if target element can be location, return this element
        :return:
        selenium element
        """
        return WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_element_located(element_selector))

    @after_error_hook
    def finds(self, element_selector, timeout=EXPLICIT_WAIT) -> List[WebElement]:
        """
        :param  timeout:
        :param element_selector:
        if all target elements can be location, return elements list
        :return:
        selenium elements list
        """
        log.info('find element {1} by {0}'.format(*element_selector))
        return WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_all_elements_located(element_selector))

    @after_error_hook
    def click_element(self, element_selector, timeout=EXPLICIT_WAIT):
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        element = WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.element_to_be_clickable(element_selector))
        element.click()

    @after_error_hook
    def click_elements(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None):
        """
        :param element_seletctor:
        :param timeout:
        :param _slice
        :return:
        """
        log.info('click elements {1} by {0}'.format(*element_selector))
        elements = self._clickable_elements(element_selector, timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        for element in elements:
            element.click()

    @after_error_hook
    def get_element_text(self, element_selector, timeout=EXPLICIT_WAIT) -> str:
        return self.find(element_selector, timeout).text

    @after_error_hook
    def get_elements_text(self, element_selector, timeout=EXPLICIT_WAIT, _slice=None) -> List[str]:
        elements = self.finds(element_selector, timeout)
        if _slice and isinstance(_slice, slice):
            elements = elements[_slice]
        return [ele.text for ele in elements]

    @after_error_hook
    def send_value(self, element_selector, value, timeout=EXPLICIT_WAIT):
        self.find(element_selector, timeout).send_keys(value)

    @after_error_hook
    def action_chain(self):
        return ActionChains(self.driver)

    @after_error_hook
    def scroll_find(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        element = WebDriverWait(self.driver, timeout=timeout)\
            .until(EC.presence_of_element_located(element_selector))
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        return element

    @after_error_hook
    def scroll_click(self, element_selector, timeout=EXPLICIT_WAIT):
        self.scroll_find(element_selector, timeout).click()

    @contextmanager
    def switch_to_new_window_handle(self):
        '''
        when enter this context will auto switch driver to new open tab,
        exist context will auto close this tab and switch driver back to origin tab.
        :return:
        '''
        wait = WebDriverWait(self.driver, timeout=self.EXPLICIT_WAIT)
        origin_window = self.driver.current_window_handle
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in self.driver.window_handles:
            if window_handle != origin_window:
                self.driver.switch_to.window(window_handle)
                break
        yield self
        self.driver.switch_to.window(origin_window)

    @contextmanager
    def switch_to_iframe(self, element_select, timeout=EXPLICIT_WAIT):
        if isinstance(element_select, WebElement):
            iframe = element_select
        else:
            iframe = self.find(element_select, timeout)
        self.driver.switch_to.frame(iframe)
        yield self
        self.driver.close()
        self.driver.switch_to.default_content()

    def screenshot(self):
        log.info('Get screenshot.')
        return self.driver.get_screenshot_as_png()

    def element_screenshot(self, element_selector, timeout=EXPLICIT_WAIT):
        if isinstance(element_selector, WebElement):
            element = element_selector
        else:
            element = self.find(element_selector, timeout)
        log.info('Get screenshot.')
        return element.screenshot_as_png()

    def _clickable_elements(self, element_selector, timeout=EXPLICIT_WAIT) -> WebElement:
        """
        :param element_seletctor:
        :param timeout:
        :return:
        """
        elements = WebDriverWait(self.driver, timeout=timeout)\
            .until(elements_to_be_clickable(element_selector))
        return elements


class elements_to_be_clickable(object):
    """ An Expectation for checking al elements is visible and enabled such that
    you can click they."""
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        elements = EC.visibility_of_all_elements_located(self.locator)(driver)
        clickable_elements = []
        if elements:
            for element in elements:
                if element.is_enabled():
                    clickable_elements.append(element)
                else:
                    return False
            return clickable_elements
        else:
            return False
