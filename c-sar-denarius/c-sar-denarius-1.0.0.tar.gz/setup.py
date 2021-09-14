#!/usr/bin/env python3
#
# Copyright (c) 2021 Genome Research Ltd
#
# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>
#
# This file is part of c-sar-denarius.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# 1. The usage of a range of years within a copyright statement contained within
# this distribution should be interpreted as being equivalent to a list of years
# including the first and last year specified and all consecutive years between
# them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
# 2009, 2011-2012’ should be interpreted as being identical to a statement that
# reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
# statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
# identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
# 2009, 2010, 2011, 2012’.
from setuptools import setup

config = {
    "name": "c-sar-denarius",
    "description": "Interface overlay for c-sar",
    "long_description": open("README.md").read(),
    "long_description_content_type": "text/markdown",
    "author": "Keiran M Raine",
    "url": "https://github.com/cancerit/c-sar-denarius",
    "author_email": "cgphelp@sanger.ac.uk",
    "version": "1.0.0",
    "license": "AGPL-3.0",
    "python_requires": ">= 3.9",
    "install_requires": [
        "click>=8.0.1",
        "click-option-group>=0.5.3",
        "mkdocs-material>=7.2.2",
        "pyyaml>=5.4.1",
    ],
    "packages": ["c_sar_denarius"],
    "package_data": {
        "c_sar_denarius": [
            "resources/structure/*.yaml",
            "resources/templates/*",
            "resources/other/*",
        ]
    },
    "entry_points": {
        "console_scripts": ["c-sar-denarius=c_sar_denarius.cli:cli"],
    },
}

setup(**config)
