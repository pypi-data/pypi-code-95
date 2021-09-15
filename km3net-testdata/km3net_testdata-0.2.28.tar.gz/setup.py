#!/usr/bin/env python
# Filename: setup.py
"""
The km3net_testdata setup script.

"""
from setuptools import setup
import sys


def read_stripped_lines(filename):
    """Return a list of stripped lines from a file"""
    with open(filename) as fobj:
        return [line.strip() for line in fobj.readlines()]


try:
    with open("README.rst") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    long_description = "KM3NeT TestData"

setup(
    name='km3net_testdata',
    url='https://git.km3net.de/km3py/km3net-testdata',
    description='KM3NeT TestData',
    long_description=long_description,
    author='Tamas Gal',
    author_email='tgal@km3net.de',
    packages=['km3net_testdata'],
    include_package_data=True,
    platforms='any',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    python_requires='>=2.7',
    install_requires=read_stripped_lines("requirements.txt"),
    extras_require={"dev": read_stripped_lines("requirements-dev.txt")},
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
    ],
)
