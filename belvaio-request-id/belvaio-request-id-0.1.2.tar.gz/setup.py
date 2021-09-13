#!/usr/bin/env python

import os
import re

from setuptools import setup


def get_version():
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join("belvaio_request_id", "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


def get_packages():
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk("belvaio_request_id")
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


setup(
    name="belvaio-request-id",
    url="https://github.com/belvo-finance/belvaio-request-id",
    license="Apache Software License 2.0",
    version=get_version(),
    python_requires=">=3.7",
    description="An aiohttp utils to track request journey between services.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Belvo Finance, S.L.",
    author_email="hello@belvo.co",
    install_requires=[
        "aiohttp>=3.5",
    ],
    packages=get_packages(),
    package_data={"belvaio_request_id": ["py.typed"]},
    data_files=[("", ["LICENSE"])],
    extras_require={
        "sentry": [
            "sentry-sdk",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=False,
)
