#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dbaas_foxha',
    version='0.3.0',
    description="DBaaS FoxHA is a simple FoxHA api wrapper for DBaaS",
    long_description=readme + '\n\n' + history,
    author="Mauro Murari",
    author_email='mauro_murari@hotmail.com',
    url='https://github.com/globocom/dbaas-foxha',
    packages=[
        'dbaas_foxha',
    ],
    package_dir={'dbaas_foxha':
                 'dbaas_foxha'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='dbaas_foxha',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
