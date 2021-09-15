#!/usr/bin/env python3
import os
import sys
import shutil
import setuptools

# Workaround issue in pip with "pip install -e --user ."
import site
site.ENABLE_USER_SITE = True

with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="andor3",
    version="0.3.1",
    author="Patrick Tapping",
    author_email="mail@patricktapping.com",
    description="Interface to Andor s-CMOS cameras which communicate using the SDK3.",
    long_description=long_description,
    url="https://gitlab.com/ptapping/andor3",
    project_urls={
        "Documentation": "https://andor3.readthedocs.io/",
        "Source": "https://gitlab.com/ptapping/andor3",
        "Tracker": "https://gitlab.com/ptapping/andor3/-/issues",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
    ],
)
