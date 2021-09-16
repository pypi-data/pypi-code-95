#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Goddy <goddy@mykg.ai> 2021/9/16
# Desc:

from setuptools import setup, find_packages

setup(
    name="goddy",
    version="0.0.1",
    keyword=("goddy"),
    description="A test project for goddy.",
    long_description="A test project for goddy wu.",
    license="MIT Licence",

    url="https://goddywu.github.io/",
    author="goddy",
    author_email="goddy@mykg.ai",

    packages=find_packages(),
    include_package_data=True,
    platform="any",
    install_requires=[],
)
