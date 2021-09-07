import pytest
import os
from os.path import join, exists
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from syncloudlib.integration.installer import get_data_dir, get_app_dir, get_service_prefix, get_ssh_env_vars, get_snap_data_dir
from syncloudlib.integration.device import Device
from syncloudlib.integration.selenium_wrapper import SeleniumWrapper


def pytest_addoption(parser):
    parser.addoption("--domain", action="store")
    parser.addoption("--device-host", action="store")
    parser.addoption("--app-archive-path", action="store")
    parser.addoption("--app", action="store")
    parser.addoption("--ui-mode", action="store", default="desktop")
    parser.addoption("--device-user", action="store", default="user")
    parser.addoption("--build-number", action="store", default="local")
    parser.addoption("--browser", action="store", default="firefox")
    parser.addoption("--redirect-user", action="store", default="redirect-user-notset")
    parser.addoption("--redirect-password", action="store", default="redirect-password-notset")


@pytest.fixture(scope='session')
def build_number(request):
    return request.config.getoption("--build-number")
    

@pytest.fixture(scope='session')
def device_user(request):
    return request.config.getoption("--device-user")
    
    
@pytest.fixture(scope='session')
def device_password():
    return 'Password1'
    

@pytest.fixture(scope='session')
def redirect_user(request):
    return request.config.getoption("--redirect-user")


@pytest.fixture(scope='session')
def redirect_password(request):
    return request.config.getoption("--redirect-password")
    
    
@pytest.fixture(scope='session')
def app(request):
    return request.config.getoption("--app")


@pytest.fixture(scope='session')
def ui_mode(request):
    return request.config.getoption("--ui-mode")


@pytest.fixture(scope='session')
def app_archive_path(request):
    return request.config.getoption("--app-archive-path")


@pytest.fixture(scope='session')
def device_host(request):
    return request.config.getoption("--device-host")


@pytest.fixture(scope='session')
def domain(request):
    return request.config.getoption("--domain")


@pytest.fixture(scope='session')
def browser(request):
    return request.config.getoption("--browser")


@pytest.fixture(scope='session')
def app_domain(app, domain):
    return '{0}.{1}'.format(app, domain)
    

@pytest.fixture(scope="session")
def platform_data_dir():
    return get_data_dir('platform')

    
@pytest.fixture(scope="session")
def data_dir(app):
    return get_data_dir(app)


@pytest.fixture(scope="session")
def snap_data_dir(app):
    return get_snap_data_dir(app)


@pytest.fixture(scope="session")
def app_dir(app):
    return get_app_dir(app)
    

@pytest.fixture(scope="session")
def service_prefix():
    return get_service_prefix()


def new_firefox_driver(user_agent, hub_url):

    caps = DesiredCapabilities.FIREFOX.copy()
    caps['acceptSslCerts'] = True
    caps['acceptInsecureCerts'] = True
    caps['javascriptEnabled'] = True

    options = webdriver.FirefoxOptions()
    options.set_preference('app.update.auto', False)
    options.set_preference('app.update.enabled', False)
    options.set_preference("general.useragent.override", user_agent)
    options.set_preference("devtools.console.stdout.content", True)

    return webdriver.Remote(
        command_executor=hub_url,
        desired_capabilities=caps,
        options=options
    )


def new_chrome_driver(user_agent, hub_url):

    caps = DesiredCapabilities.CHROME.copy()
    caps['javascriptEnabled'] = True
    caps['acceptInsecureCerts'] = True

    options = webdriver.ChromeOptions()
    options.add_argument('user-agent={}'.format(user_agent))
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Remote(
        command_executor=hub_url,
        desired_capabilities=caps,
        options=options
    )


@pytest.fixture(scope="module")
def driver(ui_mode, browser):
    hub_url = 'http://selenium:4444/wd/hub'
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    width = 1024
    if ui_mode == "mobile":
        user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) " \
                     "AppleWebKit/528.18 (KHTML, like Gecko) " \
                     "Version/4.0 Mobile/7A341 Safari/528.16"
        width = 400

    if browser == "firefox":
        driver = new_firefox_driver(user_agent, hub_url)
    else:
        driver = new_chrome_driver(user_agent, hub_url)
    driver.set_window_rect(0, 0, width, 2000)
    return driver


@pytest.fixture(scope="session")
def ssh_env_vars(app):
    return get_ssh_env_vars(app)


@pytest.fixture(scope='function')
def device_session(device):
    return device.login()


@pytest.fixture(scope="session")
def device(domain, device_user,
           device_password, redirect_user, redirect_password, ssh_env_vars):
    return Device(domain, device_user,
                  device_password, redirect_user, redirect_password, ssh_env_vars)


@pytest.fixture(scope="session")
def log_dir(project_dir):
    dir = join(project_dir, 'log')
    if not exists(dir):
        os.mkdir(dir)
    return dir


@pytest.fixture(scope="session")
def artifact_dir(project_dir):
    dir = join(project_dir, 'artifact')
    if not exists(dir):
        os.mkdir(dir)
    return dir


@pytest.fixture(scope="session")
def screenshot_dir(artifact_dir, ui_mode):
    ui_dir = join(artifact_dir, ui_mode)
    if not exists(ui_dir):
        os.mkdir(ui_dir)
    dir = join(ui_dir, 'screenshot')
    if not exists(dir):
        os.mkdir(dir)
    return dir


@pytest.fixture(scope="module")
def selenium(driver, ui_mode, screenshot_dir, app_domain):
    return SeleniumWrapper(driver, ui_mode, screenshot_dir, app_domain)
