#!/usr/bin/python3

from setuptools import setup

from pydebcontents import __version__

config = {
    "description": "Utilities working with Debian repository Contents files",
    "author": "Stuart Prescott",
    "url": "https://salsa.debian.org/stuart/pydebcontents/",
    "download_url": "https://salsa.debian.org/stuart/pyrebcontents/",
    "author_email": "stuart@debian.org",
    "version": __version__,
    "install_requires": [
        "python-debian",
    ],
    "test_requires": [
        "pytest",
    ],
    "packages": [
        "pydebcontents",
    ],
    "scripts": [
        "py-apt-file",
    ],
    "package_data": {
        "pydebcontents": [
            "py.typed",
        ],
    },
    "name": "pydebcontents",
}

setup(**config)
