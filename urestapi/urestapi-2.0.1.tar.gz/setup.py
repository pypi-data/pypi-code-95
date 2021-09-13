#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
from io import open
import re
import sys
import subprocess
from setuptools import Command, setup, find_packages

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("urestapi/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )


def open_file(filename):
    """Open and read the file *filename*."""
    with open(filename, "r") as f:
        return f.read()


readme = open_file("README.md")

install_requirements = [
    "click >= 4.1",
    "Pygments >= 1.6",
    "prompt_toolkit>=2.0.0,<2.1.0",
    "cli_helpers[styles] >= 1.0.1",
    "PyJWT >= 0.5.2",
    "requests",
    "urllib3 >=1.21.1",
]


setup(
    name="urestapi",
    author="vkumar",
    author_email="vibhor.aim@gmail.com",
    license="BSD",
    version=version,
    packages=find_packages(),
    package_data={"urestapi": ["urestapirc", "AUTHORS"]},
    description="Uptycs Rest API call " "highlighting.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=install_requirements,
    entry_points={
        "console_scripts": ["urestapi = urestapi.main:cli"],
        "distutils.commands": ["lint = tasks:lint", "test = tasks:test"],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
