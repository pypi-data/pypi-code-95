# encoding: utf-8

import os

from klity.klity import Klity
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def before_all(context):
    # Using Klity for testing
    context.klity = Klity()

    # ~ # Using specific options to init Chrome browser
    # ~ options = webdriver.ChromeOptions()
    # ~ prefs = {"download.default_directory" : os.path.join(os.getcwd(), "files")}
    # ~ options.add_experimental_option("prefs",prefs)
    # ~ if context.klity.configuration["options"].get("headless", False):
        # ~ options.set_headless()
    # ~ context.browser = webdriver.Chrome(options=options)

    # Using specific profile to init Firefox browser
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", os.path.join(os.getcwd(), "files"))
    profile.set_preference(
        "browser.helperApps.neverAsk.openFile", ",".join((
            "application/octet-stream",
            "application/pdf",
            "application/forcedownload",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ))
    )
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", ",".join((
            "application/octet-stream",
            "application/pdf",
            "application/forcedownload",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ))
    )
    profile.set_preference("pdfjs.disabled", True)
    options = Options()
    options.headless = context.klity.configuration["options"].get("headless", False)
    context.browser = webdriver.Firefox(profile, options=options)


def after_all(context):
    context.browser.quit()


def before_feature(context, feature):
    context.klity.before_feature(context, feature)


def after_feature(context, feature):
    context.klity.after_feature(context, feature)


def before_scenario(context, scenario):
    context.klity.before_scenario(context, scenario)


def after_scenario(context, scenario):
    context.klity.after_scenario(context, scenario)


def before_step(context, step):
    context.klity.before_step(context, step)
