#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
with open("README.rst", "r") as f:
  long_description = f.read()
setup(
    name='s22rgb',
    version='0.0.0.3',
    long_description=long_description,
    author='ytkz',
    author_email='ytkz11@163.com',
    url='https://github.com/ytkz11/s22rgb',
    description=u'Sentinel 2 to three bands rgb jpg',
    packages=['s22rgb'],
    install_requires=[],
    platforms=["all"],
    license='BSD License',
)