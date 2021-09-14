from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from typing import List


class CommonTools:
    def __init__(self, driver):
        self.driver = driver

    def click_element(self, locator: WebElement):
        action = ActionChains(self.driver)
        action.click(locator).perform()

    def double_click_element(self, locator: WebElement):
        action = ActionChains(self.driver)
        action.double_click(locator).perform()

    def move_to_element(self, locator: WebElement):
        action = ActionChains(self.driver)
        action.move_to_element(locator).perform()

    def find_element(self, locator, time: int = 60) -> WebElement:
        return WebDriverWait(self.driver, time).until(EC.visibility_of_element_located(locator))

    def find_element_presence(self, locator, time: int = 60) -> WebElement:
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator))

    def find_elements(self, locator, time: int = 60) -> List[WebElement]:
        return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located(locator))

    def find_elements_visibility(self, locator, time: int = 60) -> List[WebElement]:
        return WebDriverWait(self.driver, time).until(EC.visibility_of_all_elements_located(locator))
