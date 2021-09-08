# coding: utf-8
import codecs
import os
import sys
from setuptools import setup, find_packages

# with open('README.rst', 'rb') as fp:
#     readme = fp.read()

# 版本号，自己随便写
VERSION = "3.3.5.3"

LICENSE = "MIT"

 
setup(
    name='wxauto',
    version=VERSION,
    description='Automation script for Wechat',
    author='Kyle Lou',
    author_email='tikic@qq.com',
    license=LICENSE,
    packages=find_packages(),
    url='https://github.com/cluic/wxauto',
    install_requires=[  
        "pywin32",  
        "uiautomation",
        "pyscreenshot"
        ]
)


# URL 你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的
# INSTALL_REQUIRES 模块所依赖的python模块
# 以上字段不需要都包含
