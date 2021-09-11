#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", "r") as history_file:
    history = history_file.read()

with open("requirements.txt", "r") as req_file:
    requirements = req_file.read().splitlines()

with open("requirements_dev.txt", "r") as req_file:
    test_requirements = req_file.read().splitlines()

setup(
    author="Radosław Ganczarek",
    author_email="radoslaw@ganczarek.in",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    description="Tool configuration manager",
    entry_points={
        "console_scripts": [
            "kvack=kvack.cli:main",
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="kvack",
    name="kvack",
    packages=find_packages(include=["kvack", "kvack.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/radowit/kvack",
    version="0.1.0",
    zip_safe=False,
)
