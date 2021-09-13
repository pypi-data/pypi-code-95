#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 Barcelona Supercomputing Center - Centro Nacional de
# Supercomputación (BSC-CNS)

# This file is part of MapGenerator.

# MapGenerator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MapGenerator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MapGenerator. If not, see <http://www.gnu.org/licenses/>.

from os import path
from setuptools import setup, find_packages
from mapgenerator import __version__

REQUIREMENTS = {
    'setup': [
        'pytest-runner',
        'setuptools_scm',
    ],
}

setup(
    # Application name:
    name="mapgenerator",
    license='GNU GPL v3',
    # Version number (initial):
    version=__version__,

    # Application author details:
    author="Francesco Benincasa",
    author_email="francesco.benincasa@bsc.es",

    # Packages
    package_dir={'': '.'},
    packages=['mapgenerator', 'mapgenerator.plotting'],

    # Include additional files into the package
    # include_package_data=True,
    scripts=['bin/mg', ],

    # Details
    url="https://pypi.org/project/MapGenerator",

    keywords=['earth sciences', 'weather',
              'climate', 'air quality', '2D maps'],
    description="Map Generator is a tool that provides easy to use 2D plotting functions for Earth sciences datasets.",
    #    long_description=open("README.rst").read(),
    #    long_description_content_type='text/x-rst',

    # Dependent packages (distributions)
    setup_requires=REQUIREMENTS['setup'],
    install_requires=[
        "matplotlib",
        "pandas",
        "Basemap",
        "numpy",
        "netCDF4",
        "ConfigArgParse",
        "lxml",
        "plotly",
        "chart_studio",
        "config",
    ],
    # tests_require=REQUIREMENTS['test'],

)
