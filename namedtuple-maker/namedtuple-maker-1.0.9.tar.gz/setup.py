#!/usr/bin/env python3
''' Setup file for packaging.
'''

# Imports
import pathlib
from setuptools import find_packages, setup

# Constants
# The directory that contains this file
HERE = pathlib.Path(__file__).parent
# README contents
README = (HERE / 'README.md').read_text()

# Setup
setup(
    name='namedtuple-maker',
    version='1.0.9',
    description='Easily convert iterable objects into `namedtuple` objects.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/timothyhull/namedtuple-maker',
    author='Timothy Hull',
    author_email='timothyhull@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9'
    ],
    packages=find_packages(
        exclude=(
            ['requirements', 'text'])
        ),
    include_package_data=True,
    install_requires=None
)
