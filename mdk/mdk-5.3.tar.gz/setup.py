#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""build/set up mdk"""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

version = open('VERSION', 'r').read().strip()

setup(
    author='Michael Darr',
    author_email='mdarr@matician.com',
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    description='a docker-compose helper',
    entry_points={
        'console_scripts': ['mdk=mdk.main:mdk'],
    },
    install_requires=[
        'Click>=7',
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='mdk',
    packages=find_packages(),
    python_requires='>=3',
    url='https://matician.com/',
    version=version,
)
