#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Gao
# Mail: Zion.Gao@foxmail.com
# Created Time:  2021-08-05 11:08:34
#############################################


from setuptools import setup, find_packages
import sys
import importlib
importlib.reload(sys)

setup(
    name="sanymodel",
    version="0.1.3",
    keywords=["pip", "sanymodel", "Gao"],
    description="tools for modeling and data processing",
    long_description="tools for modeling and data processing",
    license="MIT Licence",

    url="http://gitlab.sanywind.net/sanydata/sanymodel",
    author="zion",
    author_email="Zion.Gao@foxmail.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=['sanydata', 'pandas', 'arrow', 'matplotlib==3.1.3', 'plotly']
)
