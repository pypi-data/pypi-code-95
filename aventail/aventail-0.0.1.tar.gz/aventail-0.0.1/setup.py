#!/usr/bin/env python3

import os
from setuptools import setup

# load the README file and use it as the long_description for PyPI
with open('README.md', 'r') as f:
    readme = f.read()

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name="aventail",
    description="description",
    long_description=readme,
    long_description_content_type='text/markdown',
    version="0.0.1",
    author="Devron",
    author_email="",
    url="https://www.devron.ai/products",
    packages=['aventail'],
    include_package_data=True,
    python_requires=">=3.6.*",
    install_requires=['requests', 'mlflow'],
    license="license",
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['python', 'aventail', 'federated learning']
)
