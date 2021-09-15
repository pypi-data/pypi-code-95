#!/usr/bin/env python
from setuptools import setup, find_packages

try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(
    python_requires=">=3.6",
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": ["hcpi=HCPInterface.cli.base:root"],
    },
)
