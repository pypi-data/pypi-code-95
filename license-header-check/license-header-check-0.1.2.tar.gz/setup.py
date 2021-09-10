# -*- coding: utf-8 -*-
from setuptools import setup

with open("requirements.txt") as requirements:
    setup(install_requires=requirements.readlines())
