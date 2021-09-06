#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'hexer-hx',
    version = '0.0.2',
    author = 'Martin Hultén-Ashauer',
    author_email = 'hexer-info@nimdraug.com',
    description = 'a tool to help in the arcane arts of decoding and reverse engineering binary data',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = 'https://gitlab.com/hexer-py/hexer',
    license = 'MIT',

    packages = [ 'hexer' ],

    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],

    entry_points = {
        'console_scripts': [
            'hexer=hexer:main',
        ],
    },
)
