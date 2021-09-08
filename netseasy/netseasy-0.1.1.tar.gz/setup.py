#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""netseasy - Django gateway for the payemnt solution Easy from Nets
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 3.5
Topic :: Software Development :: Libraries
"""

import setuptools

version = '0.1.1'


setuptools.setup(
    name='netseasy',
    version=version,
    url='https://gitlab.com/norsktest/netseasy.git',
    maintainer_email='itdrift@norsktest.no',
    install_requires=[],
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(exclude=["tests"]),
    zip_safe=False,
)
