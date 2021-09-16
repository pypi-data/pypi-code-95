#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Goddy <goddy@mykg.ai> 2021/9/16
# Desc:

from setuptools import setup, find_packages

setup(
    name="goddy",
    version="0.0.4",
    keyword=("goddy"),
    description="A test project for goddy.",
    long_description="A test project for goddy wu.",
    license="MIT Licence",

    url="https://goddywu.github.io/",
    author="goddy",
    author_email="goddy@mykg.ai",

    packages=['goddy'],
    include_package_data=True,
    platform="any",
    install_requires=[],

    entry_points={
        'console_scripts': [
            'goddy=goddy.shell:main'
        ]
    },
)
