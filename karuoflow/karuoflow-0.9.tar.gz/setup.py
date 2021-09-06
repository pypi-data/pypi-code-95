# -*- encoding: utf-8 -*-
'''
@文件    :setup.py
@说明    :
@时间    :2020/09/01 16:24:20
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from setuptools import setup, find_packages
from karuoflow import __version__

setup(
    name="karuoflow",
    version=__version__,
    keywords=["Approval flow", "work flow"],
    description="flow tempaltes",
    long_description="support flow management",
    license="MIT Licence",

    url="https://github.com/caimmy/karuoflow",
    author="caimmy",
    author_email="caimmy@hotmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['pymysql', 'sqlalchemy', 'PyYAML']
)
