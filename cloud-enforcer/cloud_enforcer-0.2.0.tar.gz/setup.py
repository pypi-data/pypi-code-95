#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

#requirements = ['Click>=7.0', ]
with open('requirements.txt') as FH:
    requirements = FH.readlines()

test_requirements = [ ]

setup(
    author="Dimitry Dukhovny",
    author_email='dimitry@dukhovny.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Configuration enforcement dependencies for  secure microcosms in cloud environments",
    entry_points={
        'console_scripts': [
            'cloud_enforcer=cloud_enforcer.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cloud_enforcer',
    name='cloud_enforcer',
    packages=find_packages(include=['cloud_enforcer', 'cloud_enforcer.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dimitry-dukhovny/cloud_enforcer',
    version='0.2.0',
    zip_safe=False,
)
