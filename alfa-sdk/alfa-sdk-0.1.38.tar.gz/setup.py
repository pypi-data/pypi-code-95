#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re
from setuptools import setup, find_packages


requirements = [
    "requests>=2.10.0",
    "pyyaml>=3.0.0",
    "semantic_version>=2.5.0",
    "cachetools>=3.0.0",
]
dev_requirements = [
    "boto3",
    "pytest",
    "pytest-cov",
    "black",
    "pylint",
    "wb-parameter-handler",
    "responses",
]


def get_version():
    root = os.path.dirname(__file__)
    init = open(os.path.join(root, "alfa_sdk", "__init__.py")).read()
    regex = re.compile(r"""__version__ = ['"]([0-9.]+(?:a|b|rc)*[0-9]*)['"]""")
    return regex.search(init).group(1)


setup(
    name="alfa-sdk",
    version=get_version(),
    description="The ALFA SDK for Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Widget Brain",
    url="https://bitbucket.org/widgetbrain/alfa-sdk-py",
    scripts=[],
    packages=find_packages(exclude=["tests*"]),
    package_data={"alfa_sdk.common": ["data/*.json", "data/*/*.json"]},
    include_package_data=True,
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
