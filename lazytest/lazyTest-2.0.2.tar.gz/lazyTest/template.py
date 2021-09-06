# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# time     :2020/2/13  14:44
# ---------------------------------------


# conftest.py文件模板
CONFTEST = """

# -*- coding = UTF-8 -*-
# Author   :
# File     : conftest.py
# time     : 
# Describe :
# ---------------------------------------
import os
import sys
import time
import allure
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from service.LoginService import LoginService
import lazyTest

globals()["driver"] = None


def pytest_addoption(parser):
    # pytest.ini文件自定义参数配置，想要在pytest.ini存放自定义参数，必须再此定义
    parser.addini('Terminal', help='访问浏览器参数')
    parser.addini('URL', help='添加 url 访问地址参数')
    parser.addini('setUp', help='添加 登录时前置输入的参数')
    parser.addini('username', help='添加 登录时用户名参数')
    parser.addini('password', help='添加 登录时密码参数')
    parser.addini('teardown', help='添加 登录时后置输入的参数')
    parser.addini('filepath', help='添加 截图路径')
    parser.addini('logpath', help='添加 日志路径')


@pytest.fixture(scope='session')
def getdriver(pytestconfig):
    '''
    全局的夹具配置，所有用例执行之前，和所有用例执行之后
    :param pytestconfig: 用于获取pytest.ini 中的参数
    :yield: 上面代码为前置，下面代码为后置
    '''
    Terminal = pytestconfig.getini("Terminal")
    URL = pytestconfig.getini("URL")
    driver = lazyTest.WebOption(Terminal, URL)
    globals()["driver"] = driver.baseDriver
    yield driver
    driver.baseDriver.browser_close()


@pytest.fixture(scope='session', autouse=True)
def login(getdriver, pytestconfig):
    '''
    登录业务，再此配置可在运行所有用例时只登录一次
    如果不想使用将：装饰器的autouser改为False即可
    :param getdriver: 获得驱动器
    :param pytestconfig: 从pytest.ini中获得参数
    :return: 
    '''
    lo = LoginService(getdriver)
    username = pytestconfig.getini("username")
    password = pytestconfig.getini("password")
    lo.loginService_1(username, password)


@pytest.fixture(scope="function", autouse=True)
def flush_browser(getdriver):
    '''
    每个用例执行之后刷新页面
    可通过控制装饰器的scope指定影响的级别
    可通过装饰器的autouser决定是否启用
    :param getdriver: 获取驱动器
    :return: 
    '''
    yield
    getdriver.Refresh()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    '''
    用例失败截图
    :param item: 每个用例的信息 
    :return: 
    '''
    config = item.config
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        xfail = hasattr(report, 'wasxfail')
        if report.failed and not xfail:
            project = str(config.rootpath)
            filepath = config.getini("filepath")
            picture_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
            filename = project + filepath + picture_time + ".png"
            globals()["driver"].save_screenshot(filename)
            with open(filename, "rb") as f:
                file = f.read()
                allure.attach(file, "失败截图", allure.attachment_type.PNG)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    '''配置日志输入到文件的位置'''
    config = item.config
    project = str(config.rootpath)
    logpath = config.getini("logpath")
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")
    logging_plugin.set_log_path(project + logpath)
    yield

"""
# pytest.ini文件模板
PYTEST = """
[pytest]
# 控制台输出日志配置
log_cli = true
log_cli_level = INFO
log_format = %(levelname)s %(asctime)s [%(filename)s:%(lineno)-s] %(message)s
log_date_format = %Y-%M-%D %H:%M:%S
# 文件输出日志控制
log_file_level = INFO
log_file_format = %(levelname)s %(asctime)s [%(filename)s:%(lineno)-s] %(message)s
log_file_date_format = %Y-%M-%D %H:%M:%S
# 自定义参数
#---------------------------------------------------
# 配置浏览器，支持： Chrome、Firefox、Ie、Edge、PhantomJs（无头浏览器）、ChromeOptions（谷歌提供无头）、h5（支持iPhone X）
Terminal = Chrome
# 填写需要访问页面的url，此处不需要指定路由，路由在pages层指定
URL = http://buxiubuzhi:7799
# 截图存放路径，可修改，截图文件名在conftest.py文件中定义
filepath = /result/screenshot/
# 日志存放路径，可修改
logpath = /result/log/log.log
# 自定义登录参数，可根据conftest.py文件中定义的添加，如果需要其他参数，需要先在conftest.py文件中定义
username = 
password = 
"""
# main.py文件模板
MAIN = """
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lazyTest import ClearTestResult


def getPorjectPath():
    '''
    获取项目路径
    '''
    return os.path.dirname(os.path.dirname(__file__))


def clearLogAndReport():
    print("----------清空上次测试结果----------")
    path = getPorjectPath() + "/result"
    ClearTestResult(path)
    time.sleep(2)
    print("----------测试结果清空成功----------")


def runlastFailed():
    print("启动失败用例重跑")
    cmd = "pytest -s --lf {}/case --alluredir {}/result/report".format(getPorjectPath(), getPorjectPath())
    print(os.system(cmd))


def startReport():
    print("-------------启动测试报告--------------")
    cmd = "allure serve {}/result/report".format(getPorjectPath())
    print(os.system(cmd))


def startCase(cases):
    print("------------开始执行测试------------")
    cmd = "pytest -s {}/case/{} --alluredir {}/result/report".format(getPorjectPath(), cases, getPorjectPath())
    print(os.system(cmd))


def run(cases=" "):
    clearLogAndReport()
    startCase(cases)
    s = input("请选择要启用的服务:1:启动失败用例重跑;\t2：启动测试报告;")
    if s == "1":
        runlastFailed()
        s = input("是否启动测试报告:y/n")
    if s == "2" or s == "y":
        startReport()
run()
"""






TEMP = {
    "conftest": CONFTEST,
    "pytest":   PYTEST,
    "main":     MAIN,
}
