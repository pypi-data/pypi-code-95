# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# time     :2020/2/13  14:44
# ---------------------------------------

import argparse
import os, sys
from lazyTest import __version__, __description__
from lazyTest.template import TEMP
PY3 = sys.version_info[0] == 3


def main():
    """
    API test: parse command line options and run commands.
    """

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        '-v', '--version', dest='version', action='store_true',
        help="show version")

    parser.add_argument(
        '--project',
        help="Create an lazyTest automation test project.")

    args = parser.parse_args()

    # 获取版本
    if args.version:
        print("version {}".format(__version__))
        return 0

    # 创建项目
    project_name = args.project
    if project_name:
        create_scaffold(project_name)
        return 0





def create_scaffold(project_name):
    """
    create scaffold with specified project name.
    """
    if os.path.isdir(project_name):
        print("{}:Not a directory".format(project_name))
        return

    def create_folder(path):
        print("create dir:{}".format(path))
        os.makedirs(path)

    def create_file(path, file_content=""):
        print("create file:{}".format(path))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(file_content)

    create_folder(project_name)  # 创建项目目录
    # 创建目录结构
    create_folder(os.path.join(project_name, "pages"))
    create_folder(os.path.join(project_name, "service"))
    create_folder(os.path.join(project_name, "case"))
    create_folder(os.path.join(project_name, "main"))
    create_folder(os.path.join(project_name, "result"))
    create_folder(os.path.join(project_name, "result", "log"))
    create_folder(os.path.join(project_name, "result", "report"))
    create_folder(os.path.join(project_name, "result", "screenshot"))
    create_folder(os.path.join(project_name, "resources"))
    create_folder(os.path.join(project_name, "resources", "element"))
    # 创建核心文件
    create_file(os.path.join(project_name, "__init__.py"))
    create_file(os.path.join(project_name, "case", "conftest.py"), TEMP["conftest"])
    create_file(os.path.join(project_name, "pytest.ini"), TEMP["pytest"])
    create_file(os.path.join(project_name, "main", "main.py"), TEMP["main"])

