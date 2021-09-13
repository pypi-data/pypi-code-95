#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
from ipv4tree.__init__ import VERSION

setup(
    name='ipv4tree',
    version=VERSION,
    packages=['ipv4tree'],
    install_requires=['ipaddress'],
    url='https://github.com/dvolkow/ipv4tree',
    license='GPLv3',
    author='Daniel Wolkow',
    author_email='volkov12@rambler.ru',
    python_requires='>=3.6',
    description='IPv4 addresses info data structure'
)
