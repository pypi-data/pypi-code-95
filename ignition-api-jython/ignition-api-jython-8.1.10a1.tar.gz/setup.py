#!/usr/bin/env jython
# -*- coding: utf-8 -*-

"""Ignition API."""

import os
from codecs import open

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, "src", "system", "__version__.py"), "r") as f:
    exec (f.read(), about)

with open("README.md", "r", "utf-8") as f:
    readme = str(f.read())

setup(
    name=about["__title__"],
    version="{version}{cycle}".format(
        version=about["__version__"], cycle=about["__cycle__"]
    ),
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license=about["__license__"],
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: Jython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing :: Mocking",
    ],
)
