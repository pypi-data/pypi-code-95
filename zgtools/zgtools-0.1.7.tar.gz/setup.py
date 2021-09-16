#!/usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages
import sys

setup(
    name="zgtools",
    version="0.1.7",
    author="stone",
    author_email="393928715@qq.com",
    description="quant tools",
    long_description=open("README.md", encoding='utf-8').read(),
    license="MIT",
    url='https://gitee.com/l_stone/zg_tools',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)