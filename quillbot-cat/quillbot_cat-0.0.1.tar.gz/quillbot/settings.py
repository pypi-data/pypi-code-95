from selenium import webdriver
from os import environ
from pathlib import Path

home = str(Path.home())

# GECKODRIVER_PATH = "/mnt/c/Users/krist/geckodriver.exe"
# GECKODRIVER_PATH = r"C:\Users\krist\geckodriver"
GECKODRIVER_PATH = home + "/geckodriver"
print(GECKODRIVER_PATH)

QUILLBOT_DATA = {
    "url": "https://quillbot.com/",
    "login": "hoffmeier@twnty.de",
    "password": "ii9@@@NbQyj8"
}

BROWSER_OPTIONS = webdriver.FirefoxOptions()
BROWSER_OPTIONS.set_preference("dom.webdriver.override", False)
# BROWSER_OPTIONS.headless = True

KEYCLOAK_PUBLIC_KEY_VALUE = environ.get("KEYCLOAK_PUBLIC_KEY_VALUE") or "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlJtT9TaP2FKHSxMQ+ms9LwgVix/q2FJ2L1+fGkV/kJBfFzNaUXxZ7olPYOMlPy4NhfjyzL+c8dr14uhqx2OQX9RrTYiRs3Vha55PsaME1eVo87fQSxSSpnOXM5DzJFUzBkbfGQQWP3tyX1nsAn03K7+dvw6J8qQ5RNDBfRM55voK4hfKmZCCh23cCRy5SAN3uY0/qIcOPqM8+bhwkoL93uUR+v9i0s5VmT3ZWosvwx8jX/h/3OfpLOH5MTSeW9Lmi41EGNJzVaIZBa5HvDN4jtTOnam6yKXwgWnmmXBua+w7R/kUlhiEEcsEuUuWtcaIr8HnGOU5NLynv8vKygbpzwIDAQAB"
KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----".format(KEYCLOAK_PUBLIC_KEY_VALUE)
VERIFY_SIGNATURE = environ.get("VERIFY_SIGNATURE") or False

