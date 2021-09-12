#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    test_requirements = f.read().splitlines()

setup_requirements = [
    "pytest-runner",
]

setup(
    author="Nicolas Cordier",
    author_email="nicolas.cordier@numeric-gmbh.ch",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="FEMAP neutral file parser",
    entry_points={
        "console_scripts": [
            "femap_neutral_parser=femap_neutral_parser.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="femap_neutral_parser",
    name="femap_neutral_parser",
    packages=find_packages(include=["femap_neutral_parser", "femap_neutral_parser.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    version="0.8.3",
    zip_safe=False,
    url="https://framagit.org/numenic/femap_neutral_parser",
)
