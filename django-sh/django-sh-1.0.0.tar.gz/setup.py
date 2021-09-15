#!/usr/bin/env python
from setuptools import setup, find_packages

import sh

setup(
    name="django-sh",
    version=sh.__version__,
    description=sh.__doc__,
    packages=find_packages(),
    url="https://gitlab.com/jahazieldom/django-sh",
    author="admintotal-dev",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'django>=1.8;python_version>="3"',
        # 'requests;python_version>="3"',
    ],
)
