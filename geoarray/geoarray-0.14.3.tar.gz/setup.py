#!/usr/bin/env python
# -*- coding: utf-8 -*-

# geoarray, A fast Python interface for image geodata - either on disk or in memory.
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

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("geoarray/version.py") as version_file:
    exec(version_file.read(), version)

req = [
    'cartopy',
    'dill',
    'gdal>=2.1.0',
    'matplotlib',
    'numpy',
    'pandas',
    'pyepsg',  # optional dependency of cartopy, needed by geoarray
    'py_tools_ds>=0.17.6',
    'scikit-image',
    'shapely'
    ]

req_interactive_plotting = [
    'folium',
    'geojson',
    'holoviews'
]

req_setup = ['setuptools-git']

req_test = req + ["coverage", "nose", "nose2", "nose-htmloutput", "rednose", "urlchecker", "parameterized"]

req_doc = ['sphinx-argparse', 'sphinx_rtd_theme']

req_lint = ['flake8', 'pycodestyle', 'pydocstyle']

req_dev = req_setup + req_test + req_doc + req_lint

setup(
    name='geoarray',
    version=version['__version__'],
    description="Fast Python interface for geodata - either on disk or in memory.",
    long_description=readme,
    author="Daniel Scheffler",
    author_email='danschef@gfz-potsdam.de',
    url='https://git.gfz-potsdam.de/danschef/geoarray',
    packages=find_packages(exclude=['tests*']),  # searches for packages with an __init__.py and returns a list
    package_dir={'geoarray': 'geoarray'},
    include_package_data=True,
    install_requires=req,
    license="GPL-3.0-or-later",
    zip_safe=False,
    keywords=['geoarray', 'geoprocessing', 'gdal', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>3.6',
    test_suite='tests',
    tests_require=req_test,
    setup_requires=req_setup,
    extras_require={
        "interactive_plotting": req_interactive_plotting,
        "doc": req_doc,
        "test": req_test,
        "lint": req_lint,
        "dev": req_dev
    }
)
