#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  8/24/2021 1:35 PM
@Desc    :  Scaffold Generator.
"""

import os
import platform
import sys

from loguru import logger


class ExtraArgument:
    create_venv = False


def init_parser_scaffold(subparsers):
    sub_parser_scaffold = subparsers.add_parser(
        "startproject", help="Create a new project with template structure."
    )
    sub_parser_scaffold.add_argument(
        "project_name", type=str, nargs="?", help="Specify new project name."
    )
    sub_parser_scaffold.add_argument(
        "-venv",
        dest="create_venv",
        action="store_true",
        help="Create virtual environment in the project, and install utx.",
    )
    return sub_parser_scaffold


def create_scaffold(project_name):
    """ Create scaffold with specified project name.
    """
    if os.path.isdir(project_name):
        logger.warning(
            f"Project folder {project_name} exists, please specify a new project name."
        )
        return 1
    elif os.path.isfile(project_name):
        logger.warning(
            f"Project name {project_name} conflicts with existed file, please specify a new one."
        )
        return 1

    logger.info(f"Create new project: {project_name}")
    print(f"Project root dir: {os.path.join(os.getcwd(), project_name)}\n")

    def create_folder(path):
        os.makedirs(path)
        msg = f"Created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"Created file: {path}"
        print(msg)

    create_folder(project_name)
    create_folder(os.path.join(project_name, "config"))
    create_folder(os.path.join(project_name, "logs"))
    create_folder(os.path.join(project_name, "packages"))
    create_folder(os.path.join(project_name, "report/airtest"))
    create_folder(os.path.join(project_name, "tests"))
    create_folder(os.path.join(project_name, "suites"))

    content = """venv
.idea/
.pytest_cache
*/*__pycache__/
report
debug
*.pyc
"""
    create_file(os.path.join(project_name, ".gitignore"), content)

    content = """# UTX

---
## 安装
- 命令行执行
```
pip install utx
```

---
## 设计理念

很大程度上借鉴了HttpRunner（优秀的框架）。不同的是，utx更着重写python，而不是写YAML文件。

- 简单是更好的
- 每个人都能用python写自动化

这就是utx的设计理念。

---
## 项目结构
```
├── config
│   ├── __init__.py
│   ├── conf.py
│   └── config.ini
├── conftest.py
├── logs
├── packages
├── pytest.ini
├── report
│   ├── airtest
│   └── summary_template.html
├── requirements.txt
├── run.py
├── suites
└── tests
    ├── __init__.py
    └── test_devices.py

```

- utx提供了快速创建项目的能力，也就是脚手架。
```shell
utx startproject project_name
```
```
$ utx startproject demo
2021-09-01 12:39:16.491 | INFO     | utx.cli.scaffold:create_scaffold:51 - Create new project: demo
Project root dir: /PycharmProjects/demo

Created folder: demo
Created folder: demo/config
Created folder: demo/logs
Created folder: demo/packages
Created folder: demo/report/airtest
Created folder: demo/tests
Created folder: demo/suites
Created file: demo/.gitignore
Created file: demo/conftest.py
Created file: demo/pytest.ini
Created file: demo/run.py
Created file: demo/requirements.txt
Created file: demo/config/conf.py
Created file: demo/config/config.ini
Created file: demo/config/__init__.py
Created file: demo/tests/test_devices.py
Created file: demo/tests/__init__.py
Created file: demo/report/summary_template.html

```

---
## 专注于写脚本

- 项目结构很清晰。在conftest.py进行一些初始化/参数化/清理工作，在suites/写测试脚本。
>在AirtestIDE中写好.air脚本，然后将文件放到suites文件中。
- 更注重平铺写脚本的方式，这样就离“每个人都能用python写自动化”更近一步。毕竟封装之后看着容易晕，我也晕。
- 去除掉框架的约束，给每个人写python的自由，在测试脚本里你可以尽情发挥你的代码风格，代码能力，千人千面。代价呢，就是代码质量参差不齐。

大胆写，能写，写出来，跑通，就已经是在写自动化，就已经是在创造价值了！

---
## 轻封装

utx尊重原生用法。

airtest的封装只通过装饰器进行了运行方式的调整，没有做任何其他的冗余修改。

- faker，造数据工具
- pytest，测试框架
- airtest，自动化测试工具
- pandas、numpy，数据处理工具

安装utx，自动就把这些开源利器安装上了，无需单独安装。未来会集成更多实用工具到utx中。

utx本身是很轻的。

---

## 使用说明

- 只需在配置文件中填好相关内容，即可运行！
```
[device_info]
device = 10.237.224.160:5555
platform = android

[app_info]
package = com.longfor.yts.test
filename = AP_1.0.5.2108261134_pre.apk

[mode]
is_all = 0

[suites]
cases = test.air


```
- 启动命令
1. 普通启动
```
python run.py
```
2. 参数化启动
```
python run.py --platform=Android --device=127.0.0.1:5555
```
>参数优先级大于配置文件
---
## 运行结果
- 报告展示

![](https://files.mdnice.com/user/17535/29b7a536-9e30-45e3-b7ed-727a2091b910.png)
"""

    create_file(os.path.join(project_name, "README.md"), content)

    content = """#!/usr/bin/python
# encoding=utf-8

\"\"\" Can only be modified by the administrator. Only fixtures are provided.
\"\"\"
import logging

import allure
import pytest

from logging import getLogger
from airtest.core.api import *
from airtest.core.helper import device_platform, ST
from tenacity import Retrying, wait_fixed, stop_after_attempt
from wda import WDAError
from config.conf import *
from run import cli_device, cli_platform

logger = getLogger(__name__)
logger.info("Get PROJECT_ROOT: {}".format(ST.PROJECT_ROOT))
app_filepath = PACKAGES_PATH + '/' + ini.getvalue('app_info', 'filename')
app_name = ini.getvalue('app_info', 'package')


if cli_platform is None:
    platform = ini.getvalue('device_info', 'platform').lower()
    if platform in 'android':
        device_idx = ini.getvalue('device_info', 'device')
        device_uri = 'Android:///{}?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=MAXTOUCH'.format(device_idx)
    elif platform in 'ios':
        device_idx = ini.getvalue('device_info', 'device')
        device_uri = 'iOS:///{}'.format(device_idx)

elif cli_platform is not None:
    if cli_platform.lower() in 'android':
        device_idx = cli_device
        device_uri = 'Android:///{}?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=MAXTOUCH'.format(device_idx)
    elif cli_platform.lower() in 'ios':
        device_idx = cli_device
        device_uri = 'iOS:///{}'.format(device_idx)


def my_before_sleep(retry_state):
    if retry_state.attempt_number < 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING

    logging.log(
        loglevel,
        'Retrying %s: attempt %s ended with: %s',
        retry_state.fn,
        retry_state.attempt_number,
        retry_state.outcome,
    )


@allure.step("Try to link the device！")
def my_retry_connect(uri=None, whether_retry=True, sleeps=10, max_attempts=3):
    if not whether_retry:
        max_attempts = 1

    r = Retrying(wait=wait_fixed(sleeps), stop=stop_after_attempt(max_attempts), before_sleep=my_before_sleep,
                 reraise=True)
    try:
        return r(connect_device, uri)
    except Exception as e:
        if isinstance(e, (WDAError,)):
            logger.info("Can't connect iphone, please check device or wda state!")
        logger.info("Try connect device {} 3 times per wait 10 sec failed.".format(uri))
        raise e
    finally:
        logger.info("Retry connect statistics: {}".format(str(r.statistics)))


@allure.step("Switch to current device！")
def ensure_current_device():
    idx = device_idx
    if device().uuid != idx:
        set_current(idx)


@allure.step("Try to wake up the current device！")
def wake_device(current_device):
    current_device.wake()


@pytest.fixture(scope="session", autouse=True)
def app_fixture(request):
    with allure.step("Initialize and generate APP object！"):
        logger.info("Session start test.")
        ST.THRESHOLD = 0.7
        ST.OPDELAY = 0.25
        ST.FIND_TIMEOUT = 10
        ST.FIND_TIMEOUT_TMP = 2
        ST.SNAPSHOT_QUALITY = 10

        try:
            app = None

            app = my_retry_connect(device_uri)
            install(app_filepath)

        except Exception as e:
            logger.error("Create app fail: {}".format(e))
            allure.attach(body='',
                          name="Create app fail: {}".format(e),
                          attachment_type=allure.attachment_type.TEXT)
            pytest.exit("Create app fail: {}".format(e))

        assert (app is not None)

        ensure_current_device()

        logger.info("Current test platform: {}".format(device_platform()))
        logger.info("start app {0} in {1}:{2}".format(app_name, device_platform(), G.DEVICE.uuid))

        wake_device(G.DEVICE)

    def teardown_test():
        with allure.step("Teardown session"):
            stop_app(app_name)
            uninstall(app_name)
            pass

        logger.info("Session stop test.")

    request.addfinalizer(teardown_test)

    return app
"""
    create_file(os.path.join(project_name, "conftest.py"), content)

    content = """[pytest]
log_cli=true
log_cli_level=INFO
log_format = %(asctime)s [%(levelname)-5s] %(name)s %(funcName)s : %(message)s
log_date_format = %Y-%m-%d %H:%M:%S

# show all extra test summary info
addopts = -ra
testpaths = tests
python_files = test_devices.py
"""
    create_file(os.path.join(project_name, "pytest.ini"), content)

    content = """#!/usr/bin/python
# encoding=utf-8
\"\"\" Can only be modified by the administrator. Only Runner are provided.
\"\"\"
import os
import pytest
from utx.cli.cli import cli_env

from config.conf import ALLURE_REPORT_PATH
from utx.core.utils.tools import allure_report

cli_device, cli_platform = cli_env()

if __name__ == '__main__':
    report_path = ALLURE_REPORT_PATH + os.sep + "result"
    report_html_path = ALLURE_REPORT_PATH + os.sep + "html"
    pytest.main(["-s", "--alluredir", report_path, "--clean-alluredir"])
    allure_report(report_path, report_html_path)
"""

    create_file(os.path.join(project_name, "run.py"), content)

    content = """# Customize third-parties
# pip install --default-timeout=6000 -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

"""
    create_file(os.path.join(project_name, "requirements.txt"), content)

    content = """#!/usr/bin/python
# encoding=utf-8
\"\"\" Can only be modified by the administrator. Only Path are provided.
\"\"\"
import os

# 项目目录
from utx.core.utils.tools import ReadConfig

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置文件
INI_PATH = os.path.join(BASE_DIR, 'config', 'config.ini')

# 报告样式目录
CSS_PATH = os.path.join(BASE_DIR, 'css')

# 测试用例目录
CASE_PATH = os.path.join(BASE_DIR, 'suites')

# 日志目录
LOG_PATH = os.path.join(BASE_DIR, 'logs')

# 日志目录
PACKAGES_PATH = os.path.join(BASE_DIR, 'packages')

# allure报告目录
ALLURE_REPORT_PATH = os.path.join(BASE_DIR, 'report')

# airtest报告目录
AIRTEST_REPORT_PATH = os.path.join(BASE_DIR, 'report', 'airtest')

ini = ReadConfig(INI_PATH)

if __name__ == '__main__':
    print(ini.getvalue('app_info', 'package'))
"""

    create_file(os.path.join(project_name, "config", "conf.py"), content)

    content = """[device_info]
device = 
platform = 

[app_info]
package = 
filename = 

[mode]
is_all = 

[suites]
cases = 
"""
    create_file(os.path.join(project_name, "config", "config.ini"), content)
    create_file(os.path.join(project_name, "config", "__init__.py"))

    content = """#!/usr/bin/python
# encoding=utf-8
\"\"\" Can only be modified by the administrator. Only Cases are provided.
\"\"\"
import io
import time

import allure
import jinja2
import pytest
from utx.core.utils.tools import decryption

from config.conf import *
from conftest import device_uri
from utx.core.utils.runner import run_air

device_address = [device_uri]
cases_list = sorted(os.listdir(CASE_PATH))
cases = []
results = []
result_list = []

status = ini.getvalue('mode', 'is_all')
flag = ini.getvalue('suites', 'cases')
app_name = ini.getvalue('app_info', 'package')

if int(status) == 0:
    for suite in cases_list:
        if flag in suite:
            if suite.endswith(".air"):
                cases.append(suite)
else:
    for suite in cases_list:
        if suite.endswith(".air"):
            cases.append(suite)


@allure.feature("APP automation test")
class TestApp:
    @pytest.mark.parametrize("url", device_address)
    @pytest.mark.parametrize("case", cases)
    @allure.story("APP automation test")
    @allure.title("Current device:{url},Running case:{case}")
    @allure.description("APP automation test")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("Smoke testing")
    def test_ui_app(self, url, case):
        device_url = url
        result, dev = run_air(devices=device_url, case=case, app_name=app_name, log_path=LOG_PATH, case_path=CASE_PATH,
                              base_dir=BASE_DIR,
                              static_dir=decryption('aHR0cDovL3gubG9uZ2Zvci5zaXQvc3RhdGljL2Nzcy8='))
        result_list.append(result)
        summary_info = {'devices': dev, 'result': result_list}
        results.append(summary_info)
        print(results)
        assert result['result'] is True

    @allure.story("APP automation test")
    @allure.title("Generate test report of running device")
    @allure.description("APP automation test")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("Generate report")
    def test_report(self):

        formatList = []
        for i in results:
            if i not in formatList:
                formatList.append(i)

        for res in formatList:
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(ALLURE_REPORT_PATH),
                extensions=(),
                autoescape=True
            )
            template = env.get_template("summary_template.html", ALLURE_REPORT_PATH)
            html = template.render({"results": [res]})
            now = time.strftime("%Y-%m-%d_%H-%M-%S")
            dev = res['devices']
            output_file = os.path.join(AIRTEST_REPORT_PATH, now + '_' + dev + "_summary.html")
            with io.open(output_file, 'w', encoding="utf-8") as f:
                f.write(html)
            print(output_file)


if __name__ == "__main__":
    pytest.main(["-s", "test_devices.py"])
"""

    create_file(os.path.join(project_name, "tests", "test_devices.py"), content)
    create_file(os.path.join(project_name, "tests", "__init__.py"))
    content = """<!DOCTYPE html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link rel="icon" href="data:image/png;base64,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">
<!-- surprise form lijiawei -->
<html>

<head>
  <title>UTX Statistics</title>
  <style>
    a {
      text-decoration: none;
      color: #f6fcff;
    }
    a:hover {
    color: #94c3ee;
    text-decoration:underline;}

    body {
      font-family: "微软雅黑";
      color: #f6fcff;
      background-color: #12182A;
    }

    .fail {
      color: #ec5e5e;
      width: 7emem;
      text-align: center;
    }

    .success {
      color: #4be64b;
      width: 7emem;
      text-align: center;
    }

    .details-col-elapsed {
      width: 7em;
      text-align: center;
      height: 50px;
    }

    .details-col-msg {
      width: 7em;
      text-align: center;
      background-color: #121C34;
      height: 50px;
    }

    .title {
      text-align: center;
    }

    .table {
      margin: 0 auto;
      border: 1px #f6fcff;
      background-color: #121C34;
    }

    .text {
      text-align: center;
    }

    #td {
      text-align: center;
    }
  </style>
</head>

<body>
  <div>
    <div>
      <h2 class="title">UTX Statistics</h2>
    </div>
    <table width="800" border="thin" cellspacing="0" cellpadding="0" class="table">
      <tr width="600">
        <th width="300" class='details-col-msg'>测试用例</th>
        <th class='details-col-msg'>执行结果</th>
      </tr>
      <p class="text">运行设备：{{results[0]['devices']}}</p>
      <p class="text">{% for r in results[0]['result'] %}</p>
<!--      <p class="text">运行设备：{{r.devices}}</p>-->
      <tr>
        <td class='details-col-elapsed'>
          <a href="../../logs/{{results[0]['devices']}}/{{r.name}}/log.html" target="view_window">{{r.name}}</a>
        </td>
        <td class="{{'success' if r.result else 'fail'}}" id="td">{{"成功" if r.result else "失败"}}</td>
      </tr>
      <p class="text">{% endfor %}</p>
    </table>
  </div>
</body>

</html>
"""
    create_file(os.path.join(project_name, "report", "summary_template.html"), content)

    if ExtraArgument.create_venv:
        os.chdir(project_name)
        print("\nCreating virtual environment")
        os.system("python -m venv venv")
        print("Created virtual environment: venv")

        print("Installing utx")
        if platform.system().lower() == 'windows':
            os.chdir("venv")
            os.chdir("Scripts")
            os.system("pip install utx")
        elif platform.system().lower() == 'linux':
            os.chdir("venv")
            os.chdir("bin")
            os.system("pip install utx")
        elif platform.system().lower() == 'mac':
            os.chdir("venv")
            os.chdir("bin")
            os.system("pip install utx")


def main_scaffold(args):
    ExtraArgument.create_venv = args.create_venv
    sys.exit(create_scaffold(args.project_name))
