#!/usr/bin/env python

# Copyright 2008-2009 Canonical Ltd.
#
# This file is part of launchpadlib.
#
# launchpadlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, version 3 of the License.
#
# launchpadlib is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launchpadlib. If not, see <http://www.gnu.org/licenses/>.

"""Setup for the launchpadlib library."""

import sys
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
def generate(*docname_or_string):
    marker = '.. pypi description ends here'
    res = []
    for value in docname_or_string:
        if value.endswith('.rst'):
            with open(value) as f:
                value = f.read()
            idx = value.find(marker)
            if idx >= 0:
                value = value[:idx]
        res.append(value)
        if not value.endswith('\n'):
            res.append('')
    return '\n'.join(res)
# end generic helpers

install_requires = [
    'httplib2',
    'importlib-metadata; python_version < "3.8"',
    'keyring',
    'lazr.restfulclient>=0.9.19',
    'lazr.uri',
    'setuptools',
    'six',
    'testresources',
    'wadllib',
    ]
if sys.version < "2.6":
    install_requires.append('simplejson')

setup(
    name='launchpadlib',
    version='1.10.14',
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    author='The Launchpad developers',
    author_email='launchpadlib@lists.launchpad.net',
    maintainer='LAZR Developers',
    maintainer_email='lazr-developers@lists.launchpad.net',
    download_url= 'https://launchpad.net/launchpadlib/+download',
    description=open('README.rst').readline().strip(),
    long_description=generate(
        'src/launchpadlib/docs/index.rst',
        'NEWS.rst'),
    license='LGPL v3',
    install_requires=install_requires,
    url='https://help.launchpad.net/API/launchpadlib',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        ],
    extras_require={
        'docs': ['Sphinx'],
        'test': ['mock; python_version < "3"'],
        },
    test_suite='launchpadlib.tests',
    )
