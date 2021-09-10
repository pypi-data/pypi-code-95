# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Email:  hhczy1003@163.com
# @Date:   2017-08-01 20:37:27
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-08-01 23:05:11

from setuptools import setup

setup(
    name="easyspider",
    version="1.8.8",
    author="yiTian.zhang",
    author_email="hhczy1003@163.com",
    packages=["easyspider"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": ["easyspider = easyspider.crawler.easyspider.core.cmdline:execute"]
    }
)
