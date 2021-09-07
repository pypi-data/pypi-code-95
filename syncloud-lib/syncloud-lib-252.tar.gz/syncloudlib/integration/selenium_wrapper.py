import time

from syncloudlib.integration.screenshots import screenshots
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions


class SeleniumWrapper:
    def __init__(self, driver, ui_mode, screenshot_dir, app_domain):
        self.app_domain = app_domain
        self.screenshot_dir = screenshot_dir
        self.ui_mode = ui_mode
        self.driver = driver
        self.wait_driver = WebDriverWait(self.driver, 30)

    def find_by_xpath(self, xpath):
        self.wait_or_screenshot(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return self.driver.find_element_by_xpath(xpath)

    def find_by_name(self, name):
        self.wait_or_screenshot(expected_conditions.presence_of_element_located((By.NAME, name)))
        return self.driver.find_element_by_name(name)

    def find_by_id(self, field_id):
        self.wait_or_screenshot(expected_conditions.presence_of_element_located((By.ID, field_id)))
        return self.driver.find_element_by_id(field_id)

    def find_by_css(self, css):
        self.wait_or_screenshot(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, css)))
        return self.driver.find_element_by_css_selector(css)

    def wait_or_screenshot(self, method):
        try:
            self.wait_driver.until(method)
        except Exception as e:
            self.screenshot('exception')
            raise e

    def screenshot(self, name):
        retries = 5
        retry = 0
        while True:
            try:
                screenshots(self.driver, self.screenshot_dir, '{}-{}'.format(name, self.ui_mode))
                break
            except Exception as e:
                if retry >= retries:
                    raise
                retry += 1
                time.sleep(1)
                print('retrying screenshot {0}'.format(retry))

    def open_app(self, path=''):
        self.driver.get("https://{0}{1}".format(self.app_domain, path))
