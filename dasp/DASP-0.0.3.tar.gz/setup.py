# -*- coding: utf-8 -*-
# @Time    : 2021/9/16 15:09
# @Author  : wangzhimin！
# @FileName: setup.py
# @Blog    ：https://blog.csdn.net/qq_42197919?spm=1001.2101.3001.5343
from setuptools import setup, find_packages

setup(
    name = 'DASP',
    version = '0.0.3',
    keywords='ds caa',
    description = 'a library for DS CAA Developer',
    license = 'MIT License',
    url = 'https://blog.csdn.net/qq_42197919?spm=1001.2101.3001.5343',
    author = 'Zhimin Wang',
    author_email = '934909661@qq.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],

)