#!/usr/bin/env python
# setup.py
# vim: ai et ts=4 sw=4 sts=4 ft=python fileencoding=utf-8

import sys

from setuptools import find_packages, setup

with open("README.rst") as fh:
    long_description = fh.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "PyYAML",
]

# Python 2.6
if sys.version_info[:2] < (2, 7):
    requirements.append("argparse")

if sys.platform == "win32":
    requirements.append("pywin32")


setup(
    name="pcrunner",
    use_scm_version=True,
    description="A module for running Passive Nagios/Icinga Checks",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/maartenq/pcrunner",
    author="Maarten",
    author_email="ikmaarten@gmail.com",
    license="ISC license",
    license_file="LICENSE.txt",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Documentation :: Sphinx",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    keywords="pcrunner",
    project_urls={
        "Bug Tracker": "https://github.com/maartenq/pcrunner/issues",
        "Changelog": (
            "https://github.com/maartenq/pcrunner/blob/main/HISTORY.rst"
        ),
    },
    scripts=[
        "src/pcrunner/scripts/check_dummy.py",
        "src/pcrunner/scripts/run_check.py",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "pcrunner": [
            "etc/*",
            "data/*",
            "init/*",
            "systemd/*",
        ]
    },
    # include_package_data=True,
    entry_points={
        "console_scripts": [
            "pcrunner = pcrunner.main:main",
        ]
    },
    install_requires=requirements,
    setup_requires=[
        "setuptools>=44",
        "setuptools_scm>=5.0.2",
        "wheel",
    ],
    extras_require={
        "dev": [
            "Sphinx",
            "black",
            "build",
            "coverage",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "sphinx-rtd-theme",
            "tox",
            "twine",
        ],
        "test": [
            "pytest",
            "pytest-cov",
        ],
        "docs": [
            "Sphinx",
            "sphinx-rtd-theme",
        ],
    },
    zip_safe=False,
    test_suite="tests",
)
