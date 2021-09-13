#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import setuptools
from setuptools.command.install import install

# circleci.py version
VERSION = "v0.0.b32"

def readme():
    """print long description"""
    with open('README.rst') as f:
        return f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

setuptools.setup(
    name="argteller-viz",
    version=VERSION,
    description="Decorator for stylized interactive constructor using DSL parser",
    long_description=readme(),
    url="https://github.com/mozjay0619/argteller-viz",
    author="Jay Kim",
    author_email="mozjay0619@gmail.com",
    license="DSB 3-clause",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    # install_requires=[
    #     'requests==2.18.4',
    # ],
    python_requires='>=3',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)



