#!/usr/bin/env python3

import sys
import traceback
import json
import unittest
from setuptools import setup
from setuptools import find_packages


def get_version():
    version = {}
    with open("rockset/version.json", 'r') as vf:
        version = json.load(vf)
    return version


def get_long_description():
    with open('DESCRIPTION_sqlcli.rst', encoding='utf-8') as fd:
        long_description = fd.read()
    long_description += '\n'
    with open('RELEASE.rst', encoding='utf-8') as fd:
        long_description += fd.read()
    return long_description


# TODO: Add tests for rock-sql
setup(
    name='rockset_sqlcli',
    version=get_version().get('python', '???'),
    description='Rockset SQL REPL for `rock sql`',
    long_description=get_long_description(),
    author='Rockset, Inc',
    author_email='api@rockset.io',
    url='https://rockset.com',
    keywords="Rockset serverless search and analytics",
    packages=find_packages(include=[
        'rockset_sqlcli',
        'rockset_sqlcli.*',
    ], ),
    install_requires=[
        'cli_helpers[styles] >= 1.0.1',
        'click >= 4.1',
        'configobj >= 5.0.6',
        'humanize >= 0.5.1',
        'prompt_toolkit == 1.0.13',
        'Pygments >= 2.0',
        'pyyaml >= 3.11',
        'rockset >= 0.6.0b20190617 ',
        'sqlparse >= 0.2.2',
        'webcolors >= 1.7',
    ],
    entry_points={
        'console_scripts': ['rock-sql = rockset_sqlcli.main:main', ],
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
        'rockset_sqlcli':
            [
                'README.rst',
                'pgcli-AUTHORS',
                'pgcli-LICENSE.txt',
                'rscli/rsclirc',
                'rscli/packages/rsliterals/rsliterals.json',
            ],
    },
)
