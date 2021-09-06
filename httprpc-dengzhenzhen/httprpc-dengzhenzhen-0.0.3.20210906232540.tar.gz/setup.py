import os
import shutil
from datetime import datetime

from setuptools import setup, find_packages

# 移除构建的build文件夹
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(CUR_PATH, 'build')
if os.path.isdir(path):
    print('INFO del dir ', path)
    shutil.rmtree(path)

setup_time = datetime.now().strftime('%Y%m%d%H%M%S')

with open("C:\\Users\\Bench\\Desktop\\1.txt", 'a') as fp:
    fp.write("setup\n")

setup(
    name='httprpc-dengzhenzhen',  # 应用名
    author='dengzhenzhen',
    version='0.0.3.' + setup_time,  # 版本号
    packages=find_packages(),  # 包括在安装包内的Python包
    include_package_data=True,  # 启用清单文件MANIFEST.in,包含数据文件
    exclude_package_data={},  # 排除文件
    install_requires=[
        'Flask',
        'requests'
    ],
    entry_points={
        'console_scripts': ['runserver = setup_demo.FlaskApp:main']
    }
)
