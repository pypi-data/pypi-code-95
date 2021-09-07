from django.test import LiveServerTestCase
from selenium import webdriver

from .brython import ComponentTest


class TestComponent(LiveServerTestCase, ComponentTest):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()
