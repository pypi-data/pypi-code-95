"""
This module wrapping selenium utilities like initiate driver, basic actions, proxy server, and more
"""
import os

import allure
from selenium import webdriver
from webdrivermanager import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import ProxyType, Proxy
from bqpackage.selenium_base.selenium_actions import SeleniumActions
from bqpackage.selenium_base.selenium_storage import SeleniumStorage


@allure.step
class SeleniumConfig:
    """Default parameters for initiate driver"""

    @allure.step('Selenium driver initilaziation')
    def __init__(self, headless=False, proxy=False, storage=False, network=False):
        # TODO Change static path
        """Creates a new instance of the chrome driver.
           Starts the service and then creates new instance of chrome driver.

        :Args
        - url - set end point
        - headless - gives the option to run the tests in the background
        - proxy - gives the option to record the traffic

        :Returns:
             - the driver object"""

        self.CHROME_DRIVER_LOCATION = \
            os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'chromedriver')
        self.INSTALL_DRIVER = False
        self.PROXY_HOST = "127.0.0.1:8080"
        self.DEFAULT_URL = "chrome://settings/cookies"

        chrome_options = Options()
        capabilities = DesiredCapabilities.CHROME.copy()

        if self.INSTALL_DRIVER:
            self.install_the_latest_chrome_driver()

        if proxy:
            proxy_server = Proxy()
            proxy_server.proxy_type = ProxyType.MANUAL
            proxy_server.http_proxy = f'--proxy-server={self.PROXY_HOST}'

            chrome_options.add_argument(proxy_server.http_proxy)
            proxy_server.add_to_capabilities(capabilities)

        if network:
            capabilities = webdriver.DesiredCapabilities.CHROME
            capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

        if headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(executable_path=self.CHROME_DRIVER_LOCATION, chrome_options=chrome_options,
                                       desired_capabilities=capabilities)
        print("Started a new driver")

        if storage:
            self.storage = SeleniumStorage(self.driver)

        self.actions = SeleniumActions(self.driver)

    @allure.step
    def install_the_latest_chrome_driver(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().download_and_install())

    @allure.step
    def get_url(self, url):
        """Loads a web page in the current browser session.

        :Args:
        - driver - needs driver instance
        - url - needs end point url for start session

        :Returns:
             - the driver object"""

        try:
            self.driver.set_page_load_timeout(50)
            self.driver.get(url)
            self.driver.implicitly_wait(10)
            self.driver.maximize_window()
        except Exception as e:
            print(f'Failed to get url : {url}, reason : {e}')
            assert False

    @allure.step
    def tear_down(self):
        """close the driver session."""
        self.driver.close()
        print("driver close")

    @allure.step
    def process_browser_log_entry(self, driver):
        """print the log entry"""
        browser_log = driver.get_log('performance')
        for entry in browser_log:
            print(entry)
