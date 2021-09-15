#!/usr/bin/env python3

import sys
import traceback
import json
import unittest
from setuptools import setup
from setuptools import find_packages
import setup_tests


def get_version():
    version = {}
    with open("rockset/version.json", 'r') as vf:
        version = json.load(vf)
    return version


def get_long_description():
    with open('DESCRIPTION.rst', encoding='utf-8') as fd:
        long_description = fd.read()
    long_description += '\n'
    with open('RELEASE.rst', encoding='utf-8') as fd:
        long_description += fd.read()
    return long_description


setup(
    name='rockset',
    version=get_version().get('python', '???'),
    description='Rockset Python Client and `rock` CLI',
    long_description=get_long_description(),
    author='Rockset, Inc',
    author_email='api@rockset.io',
    url='https://rockset.com',
    keywords="Rockset serverless search and analytics",
    packages=find_packages(
        include=[
            'rockset',
            'rockset.*',
        ],
        exclude=[
            'rockset.internal',
            'rockset.internal.*',
            'rockset.rock.tests',
            'rockset.tests',
            'rockset.sql.tests',
        ],
    ),
    install_requires=[
        'docopt >= 0.6.2',
        'geojson >= 2.5.0',
        'protobuf >= 3.6.0',
        'pyyaml >= 5.1.2',
        'requests >= 2.19.0',
        'requests-toolbelt >= 0.9.1',
        'sqlalchemy >= 1.3.10',
        'texttable >= 0.8.7',
    ],
    entry_points={
        'console_scripts': ['rock = rockset.rock.main:main', ],
        # New versions
        'sqlalchemy.dialects': ['rockset= rockset.sql:RocksetDialect', ],
        # Version 0.5
        'sqlalchemy.databases': ['rockset= rockset.sql:RocksetDialect', ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Shells',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],
    package_data={
        'rockset': [
            'swagger/apiserver.yaml',
            'version.json',
        ],
    },
    test_suite='setup_tests.my_test_suite',
)
