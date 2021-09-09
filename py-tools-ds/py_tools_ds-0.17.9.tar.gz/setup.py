#!/usr/bin/env python
# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("py_tools_ds/version.py") as version_file:
    exec(version_file.read(), version)

requirements = [
    'gdal>=2.1.0',
    'geopandas',
    'numpy',
    'pandas',
    'pyproj>=2.5.0',
    'shapely',
    'spectral'
]
setup_requirements = ['setuptools']
test_requirements = requirements + ["coverage", "gdal", "nose", "nose2", "nose-htmloutput", "rednose", "shapely",
                                    "urlchecker"]

setup(
    name='py_tools_ds',
    version=version['__version__'],
    description="A collection of Python tools by Daniel Scheffler.",
    long_description=readme + '\n\n' + history,
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    url='https://git.gfz-potsdam.de/danschef/py_tools_ds',
    packages=find_packages(exclude=['tests*']),  # searches for packages with an __init__.py and returns a list
    package_dir={'py_tools_ds': 'py_tools_ds'},
    include_package_data=True,
    install_requires=requirements,
    license="GPL-3.0-or-later",
    zip_safe=False,
    keywords='py_tools_ds',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>3.6',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require={'rio_reproject': ["rasterio"]}
)
