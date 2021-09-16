# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Email:  hhczy1003@163.com
# @Date:   2017-08-01 20:37:27
# @Last Modified by:   hang.zhang
# @Last Modified time: 2017-08-01 23:05:11

from setuptools import setup

setup(
    name="easyspider",
    version="1.8.9",
    author="yiTian.zhang",
    author_email="hhczy1003@163.com",
    packages=["easyspider"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        # 上面这一段是老版本，因为带上了etl和web_ui 所以才会有crawler文件夹 新版本直接进去core就可以
        # "console_scripts": ["easyspider = easyspider.crawler.easyspider.core.cmdline:execute"]
        "console_scripts": ["easyspider = easyspider.core.cmdline:execute"]
    }
)
