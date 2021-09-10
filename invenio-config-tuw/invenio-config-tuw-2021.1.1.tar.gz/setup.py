# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing some customizations and configuration for TU Wien."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "check-manifest>=0.25",
    "coverage>=4.0",
    "isort>=4.3.3",
    "pydocstyle>=2.0.0",
    "pytest-cov>=2.5.1",
    "pytest-pep8>=1.0.6",
    "pytest-invenio>=1.2.1",
]

extras_require = {
    "docs": [
        "Sphinx>=1.5.1",
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for reqs in extras_require.values():
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=1.3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "Flask-BabelEx>=0.9.4",
    "invenio-config>=1.0.3",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_config_tuw", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-config-tuw",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio tu wien configuration",
    license="MIT",
    author="TU Wien",
    author_email="tudata@tuwien.ac.at",
    url="https://gitlab.tuwien.ac.at/fairdata/invenio-config-tuw",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "invenio_config_tuw = invenio_config_tuw:InvenioConfigTUW",
        ],
        "invenio_base.api_apps": [
            "invenio_config_tuw = invenio_config_tuw:InvenioConfigTUW",
        ],
        "invenio_base.blueprints": [
            "invenio_config_tuw = invenio_config_tuw.views:blueprint",
        ],
        "invenio_config.module": [
            # configs are loaded by invenio-config in lexicographic order
            # of their entrypoint names, and we want to override the other
            # configs here -- while not overriding invenio.cfg (which could
            # be done in the ext.init_config(app) method)
            "zzz_invenio_config_tuw = invenio_config_tuw.config",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
    ],
)
