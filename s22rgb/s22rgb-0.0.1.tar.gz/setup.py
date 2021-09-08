#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='s22rgb',
    version='0.0.1',
    author='ytkz',
    author_email='ytkz11@163.com',
    url='https://github.com/ytkz11/s22rgb',
    description=u'Sentinel 2 to three bands rgb jpg',
    packages=['s22rgb'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jujube=jujube_pill:jujube',
            'pill=jujube_pill:pill'
        ]
    }
)