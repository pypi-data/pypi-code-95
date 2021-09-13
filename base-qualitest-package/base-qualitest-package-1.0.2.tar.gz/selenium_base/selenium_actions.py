"""
This module wrapping basic selenium actions
"""
import re

import allure
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@allure.step
class SeleniumActions:

    @allure.step('Selenium actions initilaziation')
    def __init__(self, driver):
        self._list_of_elements = []
        self._web_element_type = "webelement"
        self._temp_element = None
        self._wait_seconds = 0
        self.driver = driver

    @allure.step
    def wait_for_text(self, location=None, text=None):
        try:
            if location:
                WebDriverWait(self.driver, 10).until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, location), text))
                print(f"Succes to find text: {text} in element: {location}")
            else:
                text = self.find_element_by_xpath(f"//*[text()='{text}']").text
                print(f"Succes to find text: {text}")
            return True
        except Exception:
            assert False, f"Failed to find text: {text}"

    @allure.step
    def get_list_of_elements_by_type(self, element_type, element):
        """
        - args -
              element_type: 1 = id, 2 - xpath, 3 - name, 4 - css, 5 - link text"""
        try:
            if element_type == 1:
                self._list_of_elements = self.driver.find_elements(By.ID, element)
            elif element_type == 2:
                self._list_of_elements = self.driver.find_elements(By.XPATH, element)
            elif element_type == 3:
                self._list_of_elements = self.driver.find_elements(By.NAME, element)
            elif element_type == 4:
                self._list_of_elements = self.driver.find_elements(By.CSS_SELECTOR, element)
            elif element_type == 5:
                self._list_of_elements = self.driver.find_elements(By.LINK_TEXT, element)

            return self._list_of_elements

        except Exception as e:
            print(f"Failed to find list of elements: {e}")
        return

    @allure.step
    def click(self, element, wait=0):
        sleep(wait)
        self._temp_element = self.check_all_options(element)
        try:
            if self._temp_element is not None:
                self._temp_element.click()
                print(f"success to click on element: {element}")
                return True
        except Exception as e:
            assert False, f"Failed to click on element: {e}"

    @allure.step
    def hover(self, element, wait=0):
        sleep(wait)
        self._temp_element = self.check_all_options(element)
        try:
            if self._temp_element is not None:
                hover = ActionChains(self.driver).move_to_element(self._temp_element)
                hover.perform()
                print(f"success to hover on: {element}")
                return True
        except Exception as e:
            assert False, f"Failed to hover on element ,reason: {e}"

    @allure.step
    def send_keys(self, element=None, text=None, wait=0):
        text = str(text)
        sleep(wait)
        if not element:
            ActionChains(self.driver).send_keys(text).perform()
            print(f"Succeed to send text to screen")
            return True
        self._temp_element = self.check_all_options(element)
        try:
            if self._temp_element is not None:
                self._temp_element.send_keys(text)
                print(f"Succeed to send text to element: {element}")
                return True
        except Exception as e:
            assert False, f"Failed to send text to element: {e}"

    @allure.step
    def get_text(self, element, wait=0, strip=False):
        sleep(wait)
        self._temp_element = element
        if self._web_element_type not in str(type(self._temp_element)):
            self._temp_element = self.check_all_options(element)
        try:
            if self._temp_element is not None:
                allure.attach(self._temp_element.text, 'Text', allure.attachment_type.TEXT)
                if strip:
                    return re.sub(r"\s+", "", self._temp_element.text)
                return self._temp_element.text
        except Exception as e:
            assert False, f"Failed to get text to element: {element}"

    @allure.step
    def check_all_options(self, element):
        self._temp_element = self.find_element_by_xpath(element)
        if self._temp_element is not None:
            return self._temp_element

        # check id option
        self._temp_element = self.find_element_by_id(element)
        if self._temp_element is not None:
            return self._temp_element

        # check name option
        self._temp_element = self.find_element_by_css(element)
        if self._temp_element is not None:
            return self._temp_element

        # check name option
        self._temp_element = self.find_element_by_link_text(element)
        if self._temp_element is not None:
            return self._temp_element

        # check name option
        self._temp_element = self.find_element_by_name(element)
        if self._temp_element is not None:
            return self._temp_element

        return

    @allure.step
    def find_element_by_id(self, element):
        try:
            self._temp_element = self.driver.find_element_by_id(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def find_element_by_class_name(self, element):
        try:
            self._temp_element = self.driver.find_element_by_class_name(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def find_element_by_xpath(self, element):
        try:
            self._temp_element = self.driver.find_element_by_xpath(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def find_element_by_name(self, element):
        try:
            self._temp_element = self.driver.find_element_by_name(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def find_element_by_css(self, element):
        try:
            self._temp_element = self.driver.find_element_by_css(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def find_element_by_link_text(self, element):
        try:
            self._temp_element = self.driver.find_element_by_link_text(element)
            print(f"Found element: {element}")
            return self._temp_element
        except Exception:
            print(f"Failed to find element: {element}")
        return False

    @allure.step
    def get_page_source(self):
        try:
            source = self.driver.page_source
            allure.attach(source, 'Page source', allure.attachment_type.TEXT)
            return source
        except Exception:
            return False

    @allure.step
    def get_body(self):
        try:
            allure.attach(self.driver.find_element_by_tag_name("body").text, 'Body',
                          allure.attachment_type.TEXT)
            return self.driver.find_element_by_tag_name("body").text
        except Exception:
            return False

    @allure.step
    def get_href(self, element):
        try:
            if element is not None:
                self._temp_element = element.get_attribute("href")
                allure.attach(self._temp_element, 'href', allure.attachment_type.TEXT)
                return self._temp_element

        except Exception:
            print(f"Failed to find element: {element}")
        return False
